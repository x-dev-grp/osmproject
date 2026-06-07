# Soft Delete Implementation Plan

## Objective

Standardize all business-entity deletion across the platform so that:

- `delete` means soft delete
- physical deletion is exceptional, explicit, and isolated
- all default reads exclude deleted rows
- blocked deletions return a business message instead of failing with generic errors

## Current State

### Existing foundation

- `osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/entities/BaseEntity.java`
  already provides `isDeleted`
- `osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/services/impl/BaseServiceImpl.java`
  already implements soft delete in `delete(UUID id)` by setting `isDeleted = true`
- `BaseServiceImpl.findById` and the pageable/list methods already prefer `findByIdAndIsDeletedFalse` and `findAllByIsDeletedFalse`

### Current inconsistency

The codebase currently mixes three different deletion models:

1. proper soft delete via `super.delete(...)`
2. custom soft delete via `entity.setDeleted(true)`
3. hard delete via `repository.delete(...)`, `repository.deleteById(...)`, or `baseService.remove(...)`

### Confirmed hard-delete hotspots

Representative examples:

- `osm-pack/src/main/java/com/osm/inventory_service/service/EmplacementStockService.java`
- `osm-pack/src/main/java/com/osm/inventory_service/service/BomService.java`
- `osm-cond/src/main/java/com/osm/conditioning/projet/service/ClientService.java`
- `osm-cond/src/main/java/com/osm/conditioning/shipping/service/ShippingInfoService.java`
- `osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java`
- `osm-cond/src/main/java/com/osm/conditioning/service/QCPlanService.java`
- `osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/services/impl/BaseServiceImpl.java` method `remove(UUID id)`
- `osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/controllers/impl/BaseControllerImpl.java` exposes both `remove(...)` and `delete(...)`

### Confirmed good soft-delete examples

- `osm-cond/src/main/java/com/osm/conditioning/projet/service/ProjetService.java`
- `osm-cond/src/main/java/com/osm/conditioning/service/LabelContentService.java`
- `osm-cond/src/main/java/com/osm/conditioning/service/CertificationService.java`

## Target Contract

### Backend contract

- `DELETE /resource/{id}` performs soft delete only
- `remove(...)` is not a normal business operation
- business services may override `delete(...)` only to enforce preconditions
- repositories and search endpoints exclude deleted rows by default
- restore is available only if the business entity needs reversibility

### Frontend contract

- delete buttons always call the soft-delete endpoint
- UI removes deleted entities from lists after success
- UI shows server business messages when deletion is blocked
- no frontend flow uses hard-delete semantics

### Data contract

- deleted rows remain in the table
- audit history remains intact
- unique business keys are reviewed so deleted rows do not block legitimate recreation unless that is intentional

## Design Decision

Use the existing `BaseEntity.isDeleted` and `BaseServiceImpl.delete(...)` model as the single platform standard.

Do not introduce a second soft-delete mechanism in parallel.

Do not keep hard delete reachable from normal controllers.

## Workstreams

### 1. Define deletion semantics

- `delete` = soft delete
- `remove` = purge, internal/admin-only, not used by frontend
- child line deletion must be classified case by case:
  - business/audited child entity -> soft delete
  - transient aggregate line with no standalone lifecycle -> hard remove may remain acceptable

### 2. Inventory and classify all delete paths

Create a deletion inventory grouped by:

- top-level business entity
- child entity inside aggregate
- technical cleanup only
- frontend caller
- current read filters
- current uniqueness constraints

Output: one matrix mapping every delete path to one of:

- convert to standard soft delete
- keep physical delete as internal cleanup
- deprecate/remove endpoint

### 3. Standardize service layer

For each top-level business entity:

- replace `repository.delete(...)` and `deleteById(...)` with:
  - `super.delete(id)`, or
  - a service override that validates business rules then sets `isDeleted = true`
- keep business-rule validation close to the service
- return explicit domain errors for blocked delete cases

### 4. Lock down hard delete

- restrict `remove(...)` and any direct hard-delete endpoint from normal application flows
- remove frontend usage of `remove(...)`
- if purge must remain, move it behind admin-only/internal-only access and name it explicitly as purge

### 5. Standardize reads

Review every repository/service that still uses:

- `findById(...)`
- `findAll(...)`
- custom JPQL/native SQL without `isDeleted = false`

Convert default reads to deleted-safe queries.

Special attention:

- QR resolution
- search endpoints
- dashboards
- join queries
- counts and aggregations
- lookups feeding selects/autocomplete

### 6. Resolve uniqueness and recreation rules

Soft delete changes unique-key behavior.

Review fields like:

- code
- external business identifiers
- names constrained as unique

For each unique field, decide one rule:

- deleted rows still reserve the key forever
- deleted rows no longer reserve the key

If reuse is allowed, update database indexes/constraints accordingly.

This is mandatory before broad rollout.

### 7. Frontend alignment

For each list/detail page with delete:

- verify it calls the soft-delete endpoint
- refresh local list state after delete
- display backend business messages
- ensure deleted rows disappear from default views
- add restore action only where required by business

### 8. Tests

Add automated coverage at three levels:

- service tests
  - delete sets `isDeleted = true`
  - blocked delete returns the expected business error
- controller tests
  - delete endpoint returns success without physical removal
  - deleted entity is absent from normal GET/list endpoints
- frontend tests
  - blocked delete message is shown
  - successful delete removes row from the screen

### 9. Migration and rollout

Roll out by module, not by random entity:

1. base framework and controller contract
2. inventory module
3. conditioning module
4. production module
5. frontend cleanup and final consistency pass

## Recommended Execution Sequence

### Phase 1. Framework baseline

- document platform deletion semantics
- deprecate business use of `remove(...)`
- add shared delete/restore helper patterns if needed

### Phase 2. Inventory module

- convert inventory hard-delete services first
- align frontend stock screens
- validate search, stats, and assignment flows

### Phase 3. Conditioning and production

- convert remaining business entities
- classify child-line deletion paths individually
- close repository query gaps

### Phase 4. Constraint and recovery support

- fix unique constraints impacted by soft delete
- add restore where required
- add admin purge only if a legal/operational need exists

### Phase 5. Audit and hardening

- run codebase-wide sweep for raw `delete(...)`, `deleteById(...)`, `findById(...)`, and `findAll(...)`
- verify dashboards and exports ignore deleted data by default

## Acceptance Criteria

- every business entity delete path is soft delete
- no normal frontend action physically removes a business entity
- all standard reads exclude deleted rows
- blocked deletions return explicit business messages
- unique-key behavior is defined and tested
- restore/purge behavior is explicit, restricted, and documented

## Immediate First Batch

Implement first on the entities already showing mixed behavior:

- Emplacement
- BOM
- Client
- Shipping aggregate children
- Expedition aggregate children
- QC plan children

This batch will validate the pattern before scaling it across the rest of the platform.
