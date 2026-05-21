# osm-sec

## Snapshot

- Repo: `F:\OSM PROJECT\osm-sec`
- Comparison: `main..pfe`
- Ahead/behind: `0 / 32`
- Diff size: 18 files changed, 1958 insertions, 208 deletions

## Commit Themes

- sprint1
- sprint3
- filtration-related auth expansion
- QR-era branch merge history
- local/dev and issue-fix carryover
- account activation and notification workflow additions

## Main Change Areas

- `UserController`
- `UserService`
- new DTO:
  - `VerifyOtpAndSetPasswordRequest`
- user/account models:
  - `OSMUser`
  - `ConfirmationCode`
  - `ConfirmationCodeType`
- mail infrastructure:
  - `EmailTemplateService`
  - `HtmlMailService`
  - `UserNotificationService`
- new email templates:
  - account activation
  - password reset code
  - resend activation OTP
- config updates in `application.yml`

## Interpretation

This is the highest-risk backend repo in the first pass because it changes user lifecycle logic, notification behavior, OTP handling, and account activation semantics.

The branch is doing more than one thing:

- onboarding with email OTP
- reset-password by OTP
- templated email delivery
- new activation-link generation
- user update flow evolution

That means a defect here can block login, onboarding, password recovery, or admin user management.

## Confirmed Findings

### 1. Transactional inconsistency in account activation bootstrap

In `createUserPendingConfirmation`, the disabled user is saved before email delivery:

- save user
- create OTP
- persist OTP
- send activation email

If mail sending fails with a checked exception, the method can leave a persisted disabled account and persisted OTP without rollback. This is particularly risky because the method is annotated with `@Transactional`, but checked exceptions do not trigger rollback by default.

Relevant area:

- [UserService.java](/f:/OSM%20PROJECT/osm-sec/src/main/java/com/osm/securityservice/userManagement/service/UserService.java:141)

### 2. Transactional inconsistency in reset password flow

In `resetPassword`, the reset confirmation code is persisted before notification delivery. The same rollback concern applies here.

Relevant area:

- [UserService.java](/f:/OSM%20PROJECT/osm-sec/src/main/java/com/osm/securityservice/userManagement/service/UserService.java:347)

## Risk Level

High.

This is the repo most likely to create user-facing production incidents from the current `pfe` delta.

## Review Focus For Next Pass

1. Decide whether mail send failure should roll back DB changes or be handled asynchronously.
2. Inspect all OTP lifecycle paths for replay, expiration, and duplicate-send behavior.
3. Validate account activation link generation against frontend routes.
4. Compare `main` vs `pfe` user-update behavior for credential and role side effects.

## Recommended Fix Direction

- Use explicit rollback rules, or
- Persist state and queue notifications asynchronously with a recoverable retry mechanism, or
- Split persistent state and outbound mail into a deliberate saga-like flow instead of relying on best-effort inline sending
