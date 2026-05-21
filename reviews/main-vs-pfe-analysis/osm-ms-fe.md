# osm-ms-fe

## Snapshot

- Repo: `F:\osm-ms-fe`
- Comparison: `main..pfe`
- Ahead/behind: `11 / 280`
- Diff size: extremely large
- Stat sample: 1724 files changed, 123321 insertions, 56492 deletions

## Commit Themes

- sprint 1
- filtration
- QR code
- stock by emplacement
- enum/GSON fixes
- client project work
- user flow fixes
- PWA/platformization changes

## Main Change Areas

- Angular app architecture and routing
- new OF quality-control surfaces
- labels and label workflow UI
- project/client/expedition modules
- stock, SKU, BOM, and emplacement flows
- global menu/theme/layout reshaping
- PWA assets and manifest support
- Docker and Nginx packaging
- localization growth

## Interpretation

This branch is not an incremental feature branch anymore. It is a large product branch with platform changes, UX changes, module additions, environment/config changes, and deployment changes all stacked together.

That makes code review harder because the regressions can come from:

- API coupling drift
- route drift
- environment hardcoding
- inconsistent service URL strategy
- hidden module import issues
- UI assumptions changing faster than backend contracts

## Confirmed Findings

### 1. Hardcoded backend URLs bypass environment config

Several new services directly call localhost URLs instead of building from `environment.apiUrl`.

Examples:

- [QualityService.ts](/f:/osm-ms-fe/src/app/OF/services/QualityService.ts:11)
- [BomService.ts](/f:/osm-ms-fe/src/app/stock/services/BomService.ts:11)
- [sku.service.ts](/f:/osm-ms-fe/src/app/stock/services/sku.service.ts:11)
- [stock.service.ts](/f:/osm-ms-fe/src/app/stock/services/stock.service.ts:13)

This creates deployment and portability issues in production, Docker, remote QA, and PWA usage.

### 2. Statistics service points to a different backend port

[statistique.service.ts](/f:/osm-ms-fe/src/app/stock/services/statistique.service.ts:10) uses `http://localhost:8080`, while the app environment uses `http://localhost:8084` in [environment.ts](/f:/osm-ms-fe/src/environments/environment.ts:10).

Unless this is intentional and backed by a separate exposed service, it is a direct runtime regression.

## Risk Level

Very high.

This repo has the largest branch divergence and the largest chance of hidden regressions.

## Review Focus For Next Pass

1. Normalize all API services to use `environment.apiUrl`.
2. Audit new routes and lazy-loaded modules for broken navigation paths.
3. Check feature-by-feature compatibility with backend `pfe` branches.
4. Review stock/inventory flows because they now depend on a backend that also changed heavily.
5. Review account activation/reset flows in the UI against new `osm-sec` behavior.

## Recommended Fix Direction

- First stabilize environment-driven API access
- Then review one functional area at a time:
  - auth
  - stock
  - OF/quality
  - projet/client
  - labels
