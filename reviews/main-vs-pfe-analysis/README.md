# Main vs PFE Review

This folder contains the first-pass branch review of `main` vs `pfe` across the OSM workspace.

## Scope

- Backend repos under `F:\OSM PROJECT`
- Frontend repo `F:\osm-ms-fe`
- Mobile repo `F:\osm-mobile`

## Comparison Basis

- For backend repos and `osm-ms-fe`: `main..pfe`
- For `osm-mobile`: `main..origin/pfe` because there is no local `pfe` branch

## High-Level Summary

- `osm-eureka`: no branch delta
- `osm-fin`: small delta, mostly controller exposure and config changes
- `osm-gateway`: small delta, mainly routing/config updates
- `osm-hr`: very small delta, mostly app naming/config cleanup
- `osm-pack`: large structural change, package migration plus inventory feature expansion
- `osm-parent`: large shared-library expansion, QR/global search/label support
- `osm-prod`: large domain expansion, especially filtration, genealogy, and sync
- `osm-sec`: large auth/account-flow expansion, highest backend risk in this pass
- `osm-ms-fe`: very large divergence from `main`, major product and platform changes
- `osm-mobile`: small delta, focused on QR flow, but contains an environment-specific base URL

## Confirmed Findings From This Pass

1. `osm-sec` has transactional risk in account activation and password reset flows.
   The code persists state before email delivery and uses checked exceptions, which may leave partially completed flows.

2. `osm-ms-fe` hardcodes backend URLs in several new services.
   This bypasses environment config and creates portability and deployment risk.

3. `osm-ms-fe` has one stock statistics service pointed at `localhost:8080` while the rest of the app targets `8084`.
   That looks like a direct functional regression unless a second backend is expected.

4. `osm-mobile` `origin/pfe` points its base URL to `10.0.2.2:8084`.
   That works for Android emulators but breaks physical-device usage unless the network setup is very specific.

## Files

- [osm-eureka.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-eureka.md)
- [osm-fin.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-fin.md)
- [osm-gateway.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-gateway.md)
- [osm-hr.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-hr.md)
- [osm-pack.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-pack.md)
- [osm-parent.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-parent.md)
- [osm-prod.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-prod.md)
- [osm-sec.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-sec.md)
- [osm-ms-fe.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-ms-fe.md)
- [osm-mobile.md](/f:/OSM%20PROJECT/reviews/main-vs-pfe-analysis/osm-mobile.md)

## Limitations

- This review is based on git diff inspection and targeted code reading.
- I could not run Maven validation because `mvn` is not installed in the current environment.
- I have not yet done a full end-to-end semantic verification of every new endpoint and UI path.
