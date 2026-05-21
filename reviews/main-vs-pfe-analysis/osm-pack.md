# osm-pack

## Snapshot

- Repo: `F:\OSM PROJECT\osm-pack`
- Comparison: `main..pfe`
- Ahead/behind: `0 / 23`
- Diff size: 99 files changed, 4981 insertions, 1030 deletions

## Commit Themes

- sprint3
- QR code generation
- filtration-related work
- mobile sync
- inventory fixes
- client project work

## Main Change Areas

- large package migration from `com.abiooc.inventory_service` to `com.osm.inventory_service`
- expansion of inventory domain:
  - articles
  - BOM
  - clients
  - emplacement stock
  - fournisseurs
  - SKU
  - stock movement
  - purchase orders
  - audit/statistics
- `application.yml`
- `pom.xml`

## Interpretation

This is one of the biggest backend deltas in the workspace. It is not just a feature branch; it looks like a partial productization pass where the inventory service was renamed, expanded, and repositioned to align with the rest of the OSM namespace.

The package migration increases risk because even when the code compiles, there can be hidden issues around:

- component scanning
- entity scanning
- Flyway baseline expectations
- serialized package names in generated docs or cached clients
- security/permission annotations

## Risk Level

High.

This repo has enough surface change to hide subtle startup issues and integration drift, especially because it touches controllers, entities, repositories, services, DTOs, and config all at once.

## Review Focus For Next Pass

1. Verify package migration correctness end to end.
2. Check entity/repository wiring and whether all moved classes are still discovered by Spring.
3. Validate statistics endpoints because the frontend already points to them and one FE service currently targets the wrong port.
4. Compare security exposure of new inventory endpoints against expected permissions.
5. Inspect mobile sync related backend behavior introduced around March 30.

## Current Findings

- No single confirmed line-level defect yet from this repo alone
- Structural risk is high enough that it should get a dedicated code review pass after `osm-sec`
