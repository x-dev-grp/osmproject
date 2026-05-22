# OSM Complete Flow Test Plan

Date: 2026-05-22

Scope: validate the full operational chain from oil reception to filtration, label generation, OF/project stock reservation, production closure, and expedition. This plan focuses on traceability and stock correctness.

## 1. Preconditions

- Backend services restarted after latest changes:
  - `osm-prod`
  - `osm-cond`
  - `osm-pack`
  - security/gateway services used by the frontend
- Frontend running from the correct path: `F:\osm-ms-fe`
- Traceability SQL applied:
  - `osm-prod/src/main/resources/db/migration/20260522_add_traceability_lot_table.sql`
  - `osm-cond/src/main/resources/db/migration/20260522_add_traceability_lot_columns.sql`
- Seed data loaded for:
  - articles/products
  - BOMs
  - stock
  - zones/emplacements
  - storage units
  - clients/projects
- Test user has access to production, stock, labels, OF, project, and expedition screens.

## 2. Test Data Required

Create or confirm these records:

- One unfiltered oil storage unit with enough volume, for example `5000 L`.
- One empty filtered oil storage unit with capacity greater than the expected filtered volume.
- One completed oil reception linked to the unfiltered storage unit.
- One quality control result linked to the reception.
- One packaging product, for example `Bottle 1L`.
- One sellable finished article with BOM:
  - packaging bottle
  - cap
  - label
  - carton if needed
- Enough available secondary stock for BOM components.
- One project with a client and required quantity.
- At least one OF without project, to test association later.

## 3. Reception And Source Traceability

### TC-01: Create Oil Reception

Steps:

1. Create a reception for oil or olive-to-oil production.
2. Assign the reception to the unfiltered storage unit.
3. Set quantity, supplier, date, lot number, and oil category.
4. Save and validate/approve as required by the current workflow.

Expected:

- Reception is saved.
- Storage unit volume increases.
- `OilTransaction` of type `RECEPTION_IN` exists.
- Reception remains linked to the storage unit.
- Quality/oil category is available for downstream traceability.

### TC-02: Add Quality Control

Steps:

1. Add quality control results for the reception.
2. Include at least one passing quality rule and one measured value.
3. Save results.

Expected:

- Quality results are visible from reception/detail screens.
- Reception category/quality is updated where applicable.
- Later traceability views show QC evidence.

## 4. Filtration Flow

### TC-03: Create Filtration Operation

Steps:

1. Open filtration creation.
2. Select the unfiltered source storage unit.
3. Select an empty filtered target storage unit.
4. Enter volume to filter, for example `5000 L`.
5. Save operation.

Expected:

- Operation status is `CREATED`.
- Source and target storage units are displayed correctly.
- Source lot number is captured on the operation.
- No physical stock movement happens yet.

### TC-04: Start Filtration

Steps:

1. Start the created filtration operation.

Expected:

- Operation status becomes `IN_PROGRESS`.
- Source and target volumes remain unchanged.
- Operation cannot be edited except allowed status actions.

### TC-05: Complete Filtration

Steps:

1. Complete operation with a lower volume after filtration, for example `4950 L`.
2. Save completion.

Expected:

- Operation status becomes `COMPLETED`.
- Source storage volume decreases by the original volume to filter.
- Target storage volume increases by the volume after filtration.
- Loss volume and loss percent are calculated.
- Target storage is marked as filtered oil.
- Target storage has a new filtered lot number.
- A `FILTRATION` oil transaction is created.
- A root `traceability_lot` exists for the original source.
- A child `traceability_lot` exists for the filtered target.
- No backend error:
  - no `Large Objects may not be used in auto-commit mode`
  - no null snapshot error
  - no missing lot number error

### TC-06: Filtration Traceability Page

Steps:

1. Open the filtration traceability page for the completed operation.
2. Review source deliveries/QC.
3. Click create label from this filtration.

Expected:

- Source tank, target tank, reception, and QC data are visible.
- The label page opens with the filtration operation selected.
- The selected source is editable before label creation.
- The page shows:
  - unfiltered source storage
  - filtered storage used for the label

## 5. Label Creation

### TC-07: Create Label From Filtration

Steps:

1. From the label page, confirm the filtration operation is selected.
2. Confirm filtered storage is shown as the label source.
3. Select packaging product.
4. Fill required fields:
  - legal denomination
  - lot number
  - net quantity
  - best before date
  - origin country
  - quality grade
  - responsible name/address
5. Generate the label draft.

Expected:

- Request sends:
  - `lotId = filtered target storage id`
  - `filtrationOperationId = selected filtration operation id`
  - packaging/product id
- Draft label is created.
- Label contains filtered lot traceability.
- Label source snapshots include `FILTERED_LOT`.
- Label has `traceabilityLotId` populated.

### TC-08: Edit And Finalize Label

Steps:

1. Edit draft fields.
2. Save draft.
3. Finalize label.
4. Export JSON.

Expected:

- Draft saves successfully.
- Finalization is blocked if required fields are missing.
- Once complete, status becomes `FINALIZED`.
- Exported JSON includes:
  - lot number
  - packaging info
  - traceability lot id
  - filtered lot source snapshot
  - origin/root reception evidence

## 6. Stock And BOM Reservation

### TC-09: Confirm Article BOM

Steps:

1. Open the finished article.
2. Confirm BOM exists for packaging components.
3. Confirm BOM endpoint works without backend `403`.

Expected:

- BOM loads successfully.
- Permissions are handled by frontend visibility, not backend `@PreAuthorize`.

### TC-10: Create Project Reservation

Steps:

1. Create/open a project.
2. Add article quantity.
3. Reserve stock for the project.

Expected:

- Project reservation checks available stock, not total stock.
- Reserved stock increases.
- Available stock decreases.
- Physical stock is not consumed at reservation time.

### TC-11: Update Project Quantity

Steps:

1. Increase project quantity.
2. Save.
3. Decrease project quantity.
4. Save.

Expected:

- Increasing quantity reserves only the difference.
- Decreasing quantity releases the difference.
- Stock reserved/available values stay correct.
- No negative reserved stock is possible.

### TC-12: Cancel Or Delete Project

Steps:

1. Cancel/delete a test project with reservations.

Expected:

- All project reservations are released.
- Available stock is restored.
- Physical stock quantity remains unchanged.

## 7. OF Flow

### TC-13: Create OF From Project

Steps:

1. Create an OF from the project.
2. Select filtered lot/source.
3. Confirm article/BOM.

Expected:

- OF has project id.
- OF has `lotVracId`.
- OF has `traceabilityLotId` or lazy backfills it from production genealogy.
- OF can display genealogy in detail screen.

### TC-14: Start OF

Steps:

1. Start the OF.

Expected:

- If OF belongs to project, it uses project reserved stock.
- If OF has no project, it uses available stock.
- Physical stock is not deducted yet.
- OF status becomes in progress.

### TC-15: Adjust OF While In Progress

Steps:

1. Increase planned/real quantity.
2. Save adjustment.
3. Decrease quantity.
4. Save adjustment.

Expected:

- Reservation adjusts according to the quantity difference.
- Increase fails if not enough available/reserved stock.
- Decrease releases excess reservation.
- Physical stock remains unchanged while OF is in progress.

### TC-16: Close OF

Steps:

1. Close/finish the OF.

Expected:

- Physical stock is deducted once, at closure.
- Reserved stock is consumed/reduced.
- Finished production quantity is recorded.
- OF traceability keeps:
  - filtered lot id
  - root reception id
  - quality data
  - storage source

## 8. Associating Unassigned OFs To Project

### TC-17: Create OF Without Project

Steps:

1. Create OF without assigning a project.
2. Keep it eligible for project association.

Expected:

- OF appears as unassigned.
- OF does not reserve project stock.

### TC-18: Add Unassigned OF To Existing Project

Steps:

1. Open project expedition/project OF selection screen.
2. Select existing project.
3. Add unassigned OF.

Expected:

- Unassigned OFs are visible with clear badge/hint.
- Selected unassigned OF becomes associated with the project.
- Project traceability includes the OF.
- No duplicate OF association happens.

## 9. Expedition Flow

### TC-19: Prepare Expedition

Steps:

1. Open project expedition.
2. Select project OFs and any newly associated unassigned OFs.
3. Select quantities/labels as required.
4. Save expedition draft.

Expected:

- Expedition can include project OFs.
- Expedition can include associated unassigned OFs.
- Client id is correct.
- Null project cases do not crash traceability.

### TC-20: Validate Expedition

Steps:

1. Validate/finalize expedition.

Expected:

- Expedition status is updated.
- Stock movement uses available finished stock correctly.
- Expedition traceability contains:
  - project
  - OFs
  - labels
  - filtered lot genealogy
  - reception/QC source data

## 10. Full Traceability Verification

### TC-21: Project Traceability View

Steps:

1. Open project traceability.
2. Review every OF.
3. Review every label.
4. Review source genealogy.

Expected:

- Grouping uses `traceabilityLotId` first, then `lotVracId` fallback.
- Labels show `traceabilityLotId`.
- OFs show traceability anchor.
- Root source/reception is visible.
- Filtration chain is visible.

### TC-22: OF Detail Traceability

Steps:

1. Open OF detail.
2. Review traceability card.

Expected:

- OF detail shows:
  - source lot
  - traceability lot id
  - root reception
  - filtration steps
  - final storage

### TC-23: Label Detail Traceability

Steps:

1. Open label detail.
2. Review origin chain.

Expected:

- Label detail shows:
  - filtered storage
  - root reception
  - quality/source proof count
  - filtration chain

## 11. Negative Tests

### TC-24: Complete Filtration With Insufficient Source Volume

Expected:

- Completion fails with clear business message.
- No storage movement occurs.
- No traceability lot is created.

### TC-25: Complete Filtration With Target Capacity Too Small

Expected:

- Completion fails with clear business message.
- No storage movement occurs.
- No traceability lot is created.

### TC-26: Generate Label Without Filtered Source

Expected:

- Frontend blocks generation with a clear message.
- Backend rejects request if `lotId` is missing.

### TC-27: Start OF Without Enough Stock

Expected:

- OF start fails.
- Existing reservations remain unchanged.
- Physical stock remains unchanged.

### TC-28: Close OF Twice

Expected:

- Second closure is blocked.
- Stock is not deducted twice.

### TC-29: Expedition With Missing OF Traceability

Expected:

- System attempts lazy backfill.
- If genealogy cannot be resolved, UI shows missing traceability clearly.
- Expedition should not silently lose source data.

## 12. Regression Checks

- Frontend build passes from `F:\osm-ms-fe`.
- Production backend compiles with Java 21.
- Conditioning backend compiles with Java 21.
- Inventory backend compiles with Java 21.
- BOM product endpoint no longer returns `403`.
- Stock article endpoint no longer returns unexpected `404` for seeded article ids.
- Toast interceptor shows backend success/error messages.
- Label form accepts route opened with:
  - `filtrationOperationId`
  - target storage `lotId`
  - manual selection from dropdown

## 13. Expected Final Acceptance

The flow is accepted only when this statement is true:

An expedition can be traced backward to its project, OFs, labels, filtered lot, filtration operation, filtered storage, original unfiltered storage, reception, and quality control results, while stock is reserved during project/OF planning and physically deducted only when production/expedition is actually completed.

