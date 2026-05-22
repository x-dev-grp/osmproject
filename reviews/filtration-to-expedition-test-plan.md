# Filtration To Expedition Review And Test Plan

## Scope

This document covers the end-to-end operational path from oil filtration in `osm-prod` to project expedition in `osm-cond`, including:

- filtration creation, start, completion, and genealogy
- project shipping preparation
- OF-backed expedition line creation
- traceability snapshot capture
- stock validation and stock exit at shipping
- expedition delivery, closure, and cancellation rules

It is written as a mixed review + executable test plan so the team can use it both for QA and for backend hardening.

## Services And Main Endpoints

- Filtration: `osm-prod` via `/api/production/filtration`
- Expedition: `osm-cond` via `/api/expeditions`
- Shipping info: `osm-cond` via `/api/ordreConditionement/shipping`
- Live project traceability: `/api/expeditions/project/{projectId}/traceability`

## Review Findings

### High

1. Expedition DTO and QR payload use the expedition id as `clientId`.
   - [ExpeditionService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java:203>)
   - [ExpeditionService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java:627>)
   - Impact: expedition resolve payload and normal reads can expose the wrong client identity, which breaks downstream integrations and traceability exports.

2. Expedition stock validation ignores reservations.
   - [ExpeditionService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java:487>)
   - Current code checks `quantiteActuelle`, not `quantiteDisponible`.
   - Impact: a shipment can be marked `READY` even when the free stock is already reserved for projects or OF-driven execution.

### Medium

3. OF-to-project validation can null-pointer when an OF has no project.
   - [ExpeditionService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java:469>)
   - `of.getProjet().getId()` is used without guarding `of.getProjet()`.

4. Traceability OF filtering has the same null-project risk.
   - [TraceabilityService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/TraceabilityService.java:149>)
   - Impact: snapshot capture can fail for mixed data quality instead of skipping invalid OFs cleanly.

5. Filtration validation happens before completion, but completion does not re-check source and target state.
   - [FiltrationService.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/service/FiltrationService.java:452>)
   - [FiltrationService.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/service/FiltrationService.java:170>)
   - Impact: if source or target volumes changed after creation, completion can apply stale assumptions.

### Low

6. Shipping and expedition are parallel tracks, not one controlled workflow.
   - [ShippingInfoService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/shipping/service/ShippingInfoService.java:177>)
   - [ExpeditionService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java:298>)
   - Impact: operations can report shipping progress independently of expedition stock exit unless the business process enforces discipline.

## Test Data Prerequisites

Create or identify the following data before running the suite:

1. One source storage unit with enough oil volume.
2. One empty target storage unit with enough capacity.
3. One root reception or trituration lot tied to the source tank.
4. One project with client assigned.
5. One final product and one BOM linked to packaging articles.
6. One OF linked to the project, with `lotVracId` pointing to the filtered lot.
7. Packaging stock for the OF output article.
8. At least one label content entry for the same `lotVracId`.
9. Optional: one second project reserving some of the same finished-goods stock to expose reservation conflicts during expedition.

## End-To-End Business Flow

1. Receive or produce oil into a source storage unit.
2. Create and complete a filtration into a target storage unit.
3. Use the filtered lot as `lotVracId` in an OF under a project.
4. Produce and close the OF so finished goods are available.
5. Prepare project shipping info.
6. Create an expedition for the project.
7. Add expedition lines manually or from OF context.
8. Mark expedition `READY`.
9. Validate expedition and freeze traceability snapshot.
10. Ship expedition and deduct finished-goods stock.
11. Deliver and close expedition.

## Test Matrix

### A. Filtration

#### A1. Create filtration successfully

- Endpoint: `POST /api/production/filtration`
- Input:
  - valid source
  - valid target
  - `volumeToFilter` less than or equal to source volume
  - target has enough free capacity
- Expected:
  - operation created in `CREATED`
  - source lot captured as `sourceLotNumber`
  - no storage volume updated yet

#### A2. Reject invalid create inputs

- Source equals target
- Requested volume greater than source current volume
- Target capacity exceeded
- Expected: `400` with validation message

#### A3. Start filtration

- Endpoint: `PUT /api/production/filtration/{id}/start`
- Expected:
  - status becomes `IN_PROGRESS`
  - second start attempt fails

#### A4. Complete filtration successfully

- Endpoint: `PUT /api/production/filtration/{id}/complete`
- Input:
  - `volumeAfter` between `0` and `volumeToFilter`
- Expected:
  - status becomes `COMPLETED`
  - `lossVolume` and `lossPercent` computed
  - target gets new lot number with `FI` prefix
  - target `filteredOil = true`
  - target `lastFiltrationDate` set
  - target inherits quality grade and oil variety
  - source volume reduced by `volumeToFilter`
  - target volume increased by `volumeAfter`
  - oil transaction of type `FILTRATION` created

#### A5. Completion validation edge cases

- `volumeAfter = null`
- `volumeAfter < 0`
- `volumeAfter > volumeToFilter`
- complete before start
- Expected: request rejected

#### A6. Concurrency check on completion

- Create filtration.
- Change source or target volume through another operation before completion.
- Complete filtration.
- Expected today:
  - likely succeeds using stale assumptions
- This is a known risk; log actual behavior and decide whether completion must revalidate capacity and source balance.

### B. Genealogy

#### B1. Genealogy on filtered lot

- Call production genealogy for target storage unit / filtered lot.
- Expected:
  - filtration step exists
  - target lot and source lot linked
  - root source shows reception or trituration origin

#### B2. Multi-step filtration chain

- Filter a lot twice across two tanks.
- Expected:
  - genealogy contains both filtration steps in chain order
  - root source is still reachable

#### B3. Missing genealogy fallback

- Use a lot with no matching reception or trituration root.
- Expected:
  - no crash
  - partial genealogy returned

### C. Project, OF, And Finished Goods Readiness

#### C1. Project has valid client

- Create expedition against project with client.
- Expected: expedition creation succeeds.

#### C2. Reject project without client

- Expected: expedition creation fails with explicit message.

#### C3. OF line defaults

- Add expedition line with `ofId` and no explicit quantity.
- Expected:
  - quantity defaults first from `quantiteBonne`, then from `quantiteCible`
  - lot number defaults from `of.lotVracId`

#### C4. Reject OF from another project

- Add expedition line using OF from a different project.
- Expected: request rejected.

#### C5. Null-project OF safety

- Add expedition line using OF with no project.
- Expected desired behavior:
  - reject cleanly with business error
- Expected current risk:
  - possible server error due to null project dereference

### D. Shipping Info

#### D1. Auto-create shipping info

- Fetch shipping by project through `GET /api/ordreConditionement/shipping/project/{projectId}` for a project with no shipping record yet.
- Expected:
  - shipping record created automatically
  - initial status `DRAFT`
  - `CREATED` event logged
  - QR code available

#### D2. Shipping line add and remove

- Add a packaging/final article line.
- Remove it.
- Expected:
  - article snapshot stored on add
  - line disappears on remove

#### D3. Shipping status transitions

- Allowed path:
  - `DRAFT -> READY_TO_SHIP -> IN_TRANSIT -> ARRIVED -> DELIVERED`
- Alternative allowed path:
  - `IN_TRANSIT -> DELIVERED`
- Cancellation:
  - allowed from `DRAFT` and `READY_TO_SHIP`
- Expected: invalid transitions rejected

### E. Expedition Drafting

#### E1. Create expedition draft

- Endpoint: `POST /api/expeditions`
- Expected:
  - expedition number generated
  - status `DRAFT`
  - project id and client id populated
  - QR fields populated

#### E2. DTO correctness

- Read the expedition back with `GET /api/expeditions/{id}`.
- Expected desired behavior:
  - `clientId = projet.client.id`
- Expected current behavior:
  - `clientId = expedition.id` due to mapping bug

#### E3. QR resolve correctness

- Call `GET /api/expeditions/resolve/{publicCode}`.
- Expected desired behavior:
  - payload client id matches real client
- Expected current behavior:
  - payload client id matches expedition id

#### E4. Add lines manually

- Add line with article id and quantity.
- Expected:
  - line stored
  - article snapshot captured
  - expedition remains editable

#### E5. Add lines from OF

- Add line with `ofId`.
- Expected:
  - OF belongs to project
  - quantity defaulting works
  - article name resolves from article or finished product

#### E6. Reject non-positive quantities

- Quantity `0` or negative.
- Expected: request rejected.

### F. Expedition Ready Validation

#### F1. Mark ready with sufficient stock

- Endpoint: `POST /api/expeditions/{id}/ready`
- Expected:
  - status `READY`
  - cumulative stock is checked per article across all lines

#### F2. Reject ready with insufficient stock

- Reduce stock below required quantity.
- Expected: transition rejected with explicit article id and required quantity.

#### F3. Reservation conflict check

- Reserve part of the same article stock elsewhere.
- Keep `quantiteActuelle >= required`, but `quantiteDisponible < required`.
- Expected desired behavior:
  - expedition should be rejected
- Expected current behavior:
  - expedition may pass because validation uses `quantiteActuelle`

### G. Traceability Snapshot

#### G1. Validate expedition captures snapshot

- Endpoint: `POST /api/expeditions/{id}/validate`
- Expected:
  - status `VALIDATED`
  - `validatedAt` set
  - `traceabilitySnapshotJson` persisted
  - snapshot contains expedition metadata
  - snapshot contains OF details
  - snapshot contains oil genealogy for each `lotVracId`
  - snapshot contains label snapshots by lot

#### G2. Snapshot immutability check

- Validate expedition.
- After that, modify live label content or genealogy inputs.
- Read expedition again.
- Expected:
  - stored snapshot does not change

#### G3. Partial genealogy resilience

- Make one genealogy call fail for one lot.
- Expected:
  - snapshot still created
  - failed lot omitted or partial
  - no total validation failure unless business wants it to be strict

### H. Shipping Stock Exit

#### H1. Ship expedition successfully

- Endpoint: `POST /api/expeditions/{id}/ship`
- Expected:
  - only allowed from `VALIDATED`
  - stock exit called once per expedition line with article id
  - status becomes `SHIPPED`
  - `shippedAt` set

#### H2. Verify stock movement timing

- Before `ship`: stock unchanged
- After `validate`: stock unchanged
- After `ship`: stock reduced
- This confirms the model is "deduct on ship", not "deduct on validate".

#### H3. Duplicate article lines

- Add two expedition lines for the same article.
- Ship expedition.
- Expected:
  - two exit calls today
  - total stock reduction equals sum of both lines
- Note:
  - acceptable if inventory service is idempotent per call; otherwise aggregation before exit may be safer.

### I. Delivery, Closure, And Cancellation

#### I1. Deliver after ship

- Endpoint: `POST /api/expeditions/{id}/deliver`
- Expected:
  - only allowed from `SHIPPED`
  - status `DELIVERED`
  - `deliveredAt` set

#### I2. Close after ship or delivery

- Endpoint: `POST /api/expeditions/{id}/close`
- Expected:
  - allowed from `SHIPPED` or `DELIVERED`
  - status `CLOSED`
  - `closedAt` set

#### I3. Cancel before ship

- Cancel from `DRAFT`, `READY`, or `VALIDATED`.
- Expected:
  - status `CANCELLED`
  - no stock exit performed

#### I4. Reject cancel after ship

- Try to cancel from `SHIPPED`, `DELIVERED`, and `CLOSED`.
- Expected: request rejected.

### J. Read APIs And Traceability Views

#### J1. Live project traceability

- Endpoint: `GET /api/expeditions/project/{projectId}/traceability`
- Expected:
  - current live OF list returned
  - current genealogy returned
  - current labels grouped by lot

#### J2. Expedition QR resolve

- Resolve expedition QR code.
- Expected:
  - `entityType = EXPEDITION`
  - web route points to project expedition page
  - data payload contains lines and status

#### J3. Shipping QR resolve

- Resolve shipping QR code.
- Expected:
  - `entityType = SHIPPING`
  - web route points to project shipping page

## Suggested Automation Split

### Fast service-level tests

- `FiltrationService`
  - create, start, complete, invalid complete
  - genealogy chain with mocked repositories
- `ExpeditionService`
  - create, addLine, markReady, validate, ship, cancel
  - DTO mapping assertions
- `TraceabilityService`
  - snapshot capture with partial genealogy success/failure
- `ShippingInfoService`
  - auto-create, line add/remove, valid/invalid status transitions

### Integration tests

- filtration completion updates tank volumes and writes filtration transaction
- expedition validate stores traceability snapshot JSON
- expedition ship triggers inventory stock exits
- live project traceability endpoint returns combined OF + genealogy + labels

### Manual UAT

- one complete business rehearsal from filtered lot to delivered expedition
- one stock-conflict rehearsal with reserved finished goods
- one corrupted-data rehearsal with OF lacking project link

## Recommended Fixes Before Trusting The Flow In Production

1. Fix expedition `clientId` mapping in DTO and QR payload.
2. Switch expedition stock validation from `quantiteActuelle` to `quantiteDisponible`.
3. Null-guard OF project access in `ExpeditionService` and `TraceabilityService`.
4. Revalidate source volume and target capacity again during filtration completion.
5. Decide whether shipping and expedition should stay parallel or whether one must gate the other.

## Minimal Regression Pack

If we need a short must-run suite before release, run these first:

1. Filtration create -> start -> complete with genealogy check.
2. OF-linked expedition line creation for same project.
3. Expedition `READY -> VALIDATED -> SHIPPED` with stock deduction only at ship.
4. Traceability snapshot immutability after validation.
5. Expedition readiness failure when only reserved stock remains.
6. Expedition DTO and QR resolve return the real client id.
