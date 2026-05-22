# OSM Progress Recap - 2026-05-22

## Scope covered
- Traceability flow from reception to filtration to labeling.
- Stock/reservation logic around OF and project usage.
- Frontend traceability and label cleanup (no UUID display).
- Post-filtration quality-control result support (backend + frontend integration points).

## Completed work

### 1) Stock / reservation / OF flow
- Reservation consumption logic tightened in inventory flow (`consommerReservation` behavior aligned to reserved quantities).
- OF lifecycle updates now correctly:
  - reserve/adjust quantities while in progress,
  - release reservations on cancel/delete,
  - consume physical stock at closure.
- Project/OF relationship flow updated so OF without project can be associated to existing project.

### 2) Traceability model hardening
- Added traceability lot backbone for filtered oil genealogy:
  - root lot resolution from source storage/reception,
  - filtered lot creation at filtration completion,
  - parent chain for genealogy.
- Filtration completion flow now preserves traceability source before source tank mutation.
- Genealogy retrieval supports traceability lot anchor and fallback legacy chain.

### 3) Label generation / detail behavior
- Label generation tied to filtration + target lot with better source mapping.
- Label stores/uses `traceabilityLotId` for stronger lineage.
- Label detail page improved:
  - removed UUID exposure,
  - cleaner display labels,
  - realistic fallback behavior (avoid fake compliance text),
  - better quality-grade display labels.
- Frontend interceptor added to pass backend success/error messages to toast service.

### 4) Filtration traceability UI
- Filtration traceability page refactored to use production genealogy model.
- Root source and quality evidence rendering improved.
- No UUID-like strings shown to users in targeted traceability/label views.

### 5) Post-filtration QC support (new)
- Added linkage fields on QC results in production service:
  - `filtrationOperationId`
  - `traceabilityLotId`
- Added backend endpoints:
  - `POST /api/production/qualitycontrolresult/filtration/{filtrationOperationId}/save-batch`
  - `GET /api/production/qualitycontrolresult/filtration/{filtrationOperationId}`
  - `GET /api/production/qualitycontrolresult/traceability-lot/{traceabilityLotId}`
- Genealogy DTO now includes filtered-lot QC payload:
  - `filteredQualityControls`
  - filtration step `qualityControls`
- Frontend models/services updated to consume this data and display it when available.

## Database scripts and setup
- Seed scripts prepared and split by database:
  - `seed-abiooc_inventory.sql`
  - `seed-osmoc.sql`
  - `seed-osmproduction.sql`
- Added migration script for filtration QC links:
  - `osm-prod/src/main/resources/db/migration/20260522_add_filtration_quality_control_links.sql`

## Known blockers / caveats
- Local backend compile verification blocked by Java toolchain mismatch:
  - project requires `--release 21`,
  - local environment does not support Java 21 currently.
- Maven also reports private package registry auth warnings (401) for snapshot metadata, though compile reaches local source compilation stage.

## Verification status
- Frontend build: `npm run build` passed (with existing non-blocking warnings already present before these changes).
- Browser validation on label page:
  - no UUID-like identifiers shown,
  - page loads without rendering errors.

## What is still pending
- Full post-filtration QC entry UI workflow:
  - action/button after filtration completion,
  - form to capture measured values per rule,
  - save through new filtration QC endpoint,
  - end-to-end validation that results appear in:
    - filtration traceability page,
    - label traceability section.
- Optional: dedicated API/controller docs for new QC endpoints.

## Recommended next step
1. Implement the post-filtration QC entry form in frontend using existing `QualityControlResultService` additions.
2. Wire auto-refresh of genealogy/label traces after save.
3. Run complete scenario test:
   - complete filtration -> add post-filtration QC -> generate label -> verify displayed QC provenance.
