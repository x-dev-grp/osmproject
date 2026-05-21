# osm-mobile

## Snapshot

- Repo: `F:\osm-mobile`
- Comparison: `main..origin/pfe`
- Ahead/behind: `1 / 2`
- Diff size: 10 files changed, 316 insertions, 109 deletions

## Commit Themes

- QR code generation

## Main Change Areas

- `MainActivity.kt`
- `ApiService.kt`
- new `QrResolveResponse.kt`
- `OfDetailActivity.kt`
- `QRScannerActivity.kt`
- `Constants.kt`
- scanner layout and strings

## Interpretation

This is a focused branch, which is good for reviewability. Most of the change is concentrated around QR scanning and code resolution workflows.

That said, even a small branch can break real usage if environment configuration is wrong.

## Confirmed Findings

### 1. Emulator-specific base URL in `origin/pfe`

The `origin/pfe` branch points the app to:

- `http://10.0.2.2:8084/`

That is appropriate for an Android emulator but not for physical devices. If the branch is intended for shared testing or release candidates, this is a portability regression.

Reference:

- `origin/pfe:app/src/main/java/com/xdev/osm_mobile/utils/Constants.kt:5`

## Risk Level

Medium.

The branch is small, but mobile environment mistakes are highly visible because they can block the whole app from authenticating or resolving scanned codes.

## Review Focus For Next Pass

1. Decide whether base URL selection should move to build flavors or environment config.
2. Trace QR scan -> resolve -> entity display flow end to end.
3. Check whether QR response models match `osm-parent` and backend QR/global-search contracts.

## Recommended Fix Direction

- Replace hardcoded device-specific base URLs with environment-aware configuration
- Validate QR paths against both emulator and real-device scenarios
