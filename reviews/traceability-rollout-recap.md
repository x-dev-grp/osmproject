# Traceability Rollout Recap

## Goal

Strengthen oil traceability from reception through filtration, conditioning, labels, and expedition by moving away from mutable storage-unit state as the main anchor.

Target chain:

`Reception -> Quality Control -> Raw Traceability Lot -> Filtration -> Filtered Traceability Lot -> OF -> Label -> Expedition`

## What We Changed

### 1. Production (`osm-prod`)

We introduced an immutable traceability backbone.

Added:

- `TraceabilityLot`
- `TraceabilitySourceType`
- `TraceabilityLotRepository`
- `TraceabilityLotService`

Files:

- [osm-prod/src/main/java/com/osm/oilproductionservice/model/TraceabilityLot.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/model/TraceabilityLot.java:1>)
- [osm-prod/src/main/java/com/osm/oilproductionservice/model/TraceabilitySourceType.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/model/TraceabilitySourceType.java:1>)
- [osm-prod/src/main/java/com/osm/oilproductionservice/repository/TraceabilityLotRepository.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/repository/TraceabilityLotRepository.java:1>)
- [osm-prod/src/main/java/com/osm/oilproductionservice/service/TraceabilityLotService.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/service/TraceabilityLotService.java:1>)

Behavior:

- root lots are created from the original reception/storage context
- filtered lots are created on filtration completion
- active lot resolution supports both direct traceability-lot ids and old storage-unit ids

Filtration now creates the immutable filtered lot:

- [osm-prod/src/main/java/com/osm/oilproductionservice/service/FiltrationService.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/service/FiltrationService.java:1>)

Genealogy now prefers immutable traceability lots, while keeping backward compatibility with old storage-unit lookups:

- [osm-prod/src/main/java/com/osm/oilproductionservice/service/GenealogyService.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/service/GenealogyService.java:1>)
- [osm-prod/src/main/java/com/osm/oilproductionservice/dto/GenealogyDto.java](</f:/OSM PROJECT/osm-prod/src/main/java/com/osm/oilproductionservice/dto/GenealogyDto.java:1>)

### 2. Conditioning backend (`osm-cond`)

We extended OF, labels, and expedition traceability to carry and prefer `traceabilityLotId`.

#### OF

Added `traceabilityLotId` to OF entity and DTO:

- [osm-cond/src/main/java/com/osm/conditioning/model/OrdreFabrication.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/model/OrdreFabrication.java:1>)
- [osm-cond/src/main/java/com/osm/conditioning/dto/OrdreFabricationDto.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/dto/OrdreFabricationDto.java:1>)

OF creation/update now resolves `traceabilityLotId` from production genealogy when `lotVracId` is set.

Legacy OFs are lazily backfilled on read.

File:

- [osm-cond/src/main/java/com/osm/conditioning/service/OFService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/service/OFService.java:1>)

#### Labels

Added `traceabilityLotId` to label persistence:

- [osm-cond/src/main/java/com/osm/conditioning/model/LabelContent.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/model/LabelContent.java:1>)
- [osm-cond/src/main/java/com/osm/conditioning/repository/LabelContentRepository.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/repository/LabelContentRepository.java:1>)

Label generation now:

- resolves genealogy from production
- stores `traceabilityLotId`
- saves a richer filtered-lot source snapshot including genealogy/root reception context

Legacy labels are lazily backfilled on read/use.

File:

- [osm-cond/src/main/java/com/osm/conditioning/service/LabelContentService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/service/LabelContentService.java:1>)

#### Expedition traceability

Expedition snapshot generation now:

- prefers `traceabilityLotId` over `lotVracId`
- groups packaged labels by immutable lot first
- backfills missing `traceabilityLotId` on OFs and labels during traceability capture

Files:

- [osm-cond/src/main/java/com/osm/conditioning/expedition/dto/GenealogyDto.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/dto/GenealogyDto.java:1>)
- [osm-cond/src/main/java/com/osm/conditioning/expedition/service/TraceabilityService.java](</f:/OSM PROJECT/osm-cond/src/main/java/com/osm/conditioning/expedition/service/TraceabilityService.java:1>)

### 3. Shared communicator DTOs (`osm-parent/comunicator`)

Added `traceabilityLotId` to shared label DTOs:

- [osm-parent/comunicator/src/main/java/com/xdev/communicator/models/shared/LabelContentDto.java](</f:/OSM PROJECT/osm-parent/comunicator/src/main/java/com/xdev/communicator/models/shared/LabelContentDto.java:1>)
- [osm-parent/comunicator/src/main/java/com/xdev/communicator/models/shared/LabelGenerateRequestDto.java](</f:/OSM PROJECT/osm-parent/comunicator/src/main/java/com/xdev/communicator/models/shared/LabelGenerateRequestDto.java:1>)

### 4. Frontend (`F:\osm-ms-fe`)

We surfaced the immutable traceability chain in the real frontend repo.

#### OF detail

Now shows:

- `traceabilityLotId`
- genealogy anchor
- root source
- root reception
- final storage lot
- filtration steps

Files:

- [F:\osm-ms-fe\src\app\OF\models\of.model.ts](</F:/osm-ms-fe/src/app/OF/models/of.model.ts:1>)
- [F:\osm-ms-fe\src\app\OF\components\of\of-detail\of-detail.component.ts](</F:/osm-ms-fe/src/app/OF/components/of/of-detail/of-detail.component.ts:1>)
- [F:\osm-ms-fe\src\app\OF\components\of\of-detail\of-detail.component.html](</F:/osm-ms-fe/src/app/OF/components/of/of-detail/of-detail.component.html:1>)
- [F:\osm-ms-fe\src\app\OF\components\of\of-detail\of-detail.component.scss](</F:/osm-ms-fe/src/app/OF/components/of/of-detail/of-detail.component.scss:1>)

#### Label detail

Now shows:

- `traceabilityLotId`
- root reception id
- filtered storage unit
- source proof count
- root source
- filtration chain

Files:

- [F:\osm-ms-fe\src\app\labels\models\label.model.ts](</F:/osm-ms-fe/src/app/labels/models/label.model.ts:1>)
- [F:\osm-ms-fe\src\app\labels\components\label-detail\label-detail.component.ts](</F:/osm-ms-fe/src/app/labels/components/label-detail/label-detail.component.ts:1>)
- [F:\osm-ms-fe\src\app\labels\components\label-detail\label-detail.component.html](</F:/osm-ms-fe/src/app/labels/components/label-detail/label-detail.component.html:1>)
- [F:\osm-ms-fe\src\app\labels\components\label-detail\label-detail.component.scss](</F:/osm-ms-fe/src/app/labels/components/label-detail/label-detail.component.scss:1>)

#### Project traceability screen

Now prefers immutable lot display and grouping cues:

- OF cards show `traceabilityLotId`
- traceability lookup uses immutable lot first
- label traceability display shows immutable lot too

Files:

- [F:\osm-ms-fe\src\app\projet\pages\projets\projet-traceability\projet-traceability.component.ts](</F:/osm-ms-fe/src/app/projet/pages/projets/projet-traceability/projet-traceability.component.ts:1>)
- [F:\osm-ms-fe\src\app\projet\pages\projets\projet-traceability\projet-traceability.component.html](</F:/osm-ms-fe/src/app/projet/pages/projets/projet-traceability/projet-traceability.component.html:1>)
- [F:\osm-ms-fe\src\app\projet\pages\projets\projet-traceability\projet-traceability.component.scss](</F:/osm-ms-fe/src/app/projet/pages/projets/projet-traceability/projet-traceability.component.scss:1>)

Added frontend genealogy model/service:

- [F:\osm-ms-fe\src\app\shared\models\production-genealogy.model.ts](</F:/osm-ms-fe/src/app/shared/models/production-genealogy.model.ts:1>)
- [F:\osm-ms-fe\src\app\shared\services\production-traceability.service.ts](</F:/osm-ms-fe/src/app/shared/services/production-traceability.service.ts:1>)

## Verification

### Backend

Backend compile verification is still blocked locally because the machine does not support Java 21:

- `osm-prod`: `release version 21 not supported`
- `osm-cond`: `release version 21 not supported`
- `osm-parent/comunicator`: `release version 21 not supported`

### Frontend

Frontend build succeeded:

- `npm run build` in `F:\osm-ms-fe`

There are pre-existing warnings:

- Sass deprecation warnings
- bundle budget warning
- unrelated Angular unused-import warnings

But the traceability UI changes did not break the build.

## Current Behavior

### New records

- filtration creates immutable production lots
- OF creation resolves and stores `traceabilityLotId`
- label creation resolves and stores `traceabilityLotId`
- expedition traceability prefers immutable lot ids

### Existing records

- older OFs with only `lotVracId` are lazily backfilled
- older labels with only `lotId` are lazily backfilled
- expedition traceability also backfills missing values during snapshot usage

## What Is Still Missing

### Highest priority

1. **Database migration scripts**
   Add explicit migrations for:
   - `traceability_lot` in production
   - `traceability_lot_id` columns in conditioning tables

   Added scripts:
   - [osm-prod/src/main/resources/db/migration/20260522_add_traceability_lot_table.sql](</f:/OSM PROJECT/osm-prod/src/main/resources/db/migration/20260522_add_traceability_lot_table.sql:1>)
   - [osm-cond/src/main/resources/db/migration/20260522_add_traceability_lot_columns.sql](</f:/OSM PROJECT/osm-cond/src/main/resources/db/migration/20260522_add_traceability_lot_columns.sql:1>)

   Important:
   - `osm-prod` and `osm-cond` do **not** currently declare Flyway/Liquibase runtime dependencies in their Maven builds.
   - So these scripts should be treated as rollout SQL for now, not as automatically executed migrations, until a migration runner is adopted.

2. **Admin visibility for legacy gaps**
   Add a report or maintenance job that shows:
   - OFs without `traceabilityLotId`
   - labels without `traceabilityLotId`
   - any genealogy lookup failures

3. **Expedition detail screen**
   The project traceability screen is updated, but expedition detail itself should expose the same chain clearly.

### Next frontend pass

1. Show immutable lot context in OF form/create flow
2. Show immutable lot context in label workflow/create flow
3. Add expedition detail traceability panel
4. Add clearer root-source/QC cards where users approve or finalize traceability-sensitive data

### Next backend pass

1. Replace remaining business dependence on `lotVracId` where possible
2. Add stricter validation for missing genealogy before final compliance-sensitive steps
3. Consider a dedicated bulk-lot lookup endpoint if frontend needs lighter-weight views than full genealogy

## Suggested Rollout Plan

### Phase 1

- complete DB migrations
- deploy production traceability lot support
- deploy conditioning support for `traceabilityLotId`

### Phase 2

- run lazy backfill in real usage
- add admin reporting for any remaining missing records
- monitor genealogy failures

### Phase 3

- expose traceability chain in expedition detail and label workflow
- train users on the new distinction:
  - `lotVracId` = operational storage/tank link
  - `traceabilityLotId` = immutable genealogy anchor

### Phase 4

- reduce reliance on mutable storage-unit state in remaining flows
- tighten compliance rules before shipment/finalization if genealogy is incomplete

## Recommended Immediate Next Step

Build the **expedition detail traceability panel** in `F:\osm-ms-fe` so users can inspect the same immutable chain directly at shipment level, not only at project level.
