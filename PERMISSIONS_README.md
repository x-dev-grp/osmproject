# OSM Roles, Permissions, and Actions

This document explains how authorization data moves through OSM, from the
security service and database seed, through JWT claims, backend entity fetches,
and frontend route/menu/action rendering.

The short version:

```text
User -> Role -> Permissions -> JWT authorities -> Frontend guards
                                      |
                                      v
                         Backend fetch attaches entity actions
```

Every permission is represented by the same key shape everywhere:

```text
MODULE:ENTITY:ACTION
```

Examples:

```text
CONDITIONING:OF:READ
CONDITIONING:OF:START
CONDITIONING:EXPEDITION:SHIP
INVENTAIR:STOCKSEC:ENTREE_STOCK
RECEPTION:UNIFIEDDELIVERY:PLANNING
```

## Core Concepts

### Module

A module is a business area. It is stored as `OSMModule` in backend Java enums,
in the permission SQL seed, and in the frontend permission enums.

Current modules:

```text
HR
RECEPTION
PRODUCTION
FINANCE
HABILITATION
INVENTAIR
CONDITIONING
```

Important files:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/OSMModule.java
osm-parent/comunicator/src/main/java/com/xdev/communicator/models/common/dtos/apiDTOs/models/OSMModule.java
osm-ms-fe/src/app/theme/types/permissions.ts
osm-prod/src/main/resources/db/migration/insert Permissions.sql
```

The SQL seed maps modules to enum ordinal values. Keep the SQL mapping aligned
with the Java enum order.

### Entity

An entity is the protected resource inside a module. Examples:

```text
OF
PROJET
EXPEDITION
STOCKSEC
ARTICLESEC
UNIFIEDDELIVERY
FINANCIALTRANSACTION
OSMUSER
ROLE
PERMISSION
```

The entity name must match across:

```text
permission.entity in the database
Controller.getResourceName()
Frontend entity enum value
Menu and route guard permission keys
```

Case is normalized to uppercase in most places, but the safest convention is to
store and use uppercase entity names.

### Action

An action is the operation granted on an entity.

Common actions:

```text
READ
CREATE
UPDATE
DELETE
```

Business actions:

```text
START
PAUSE
RESUME
CLOSE
SHIP
DELIVER
ADD_LINE
REMOVE_LINE
UPDATE_STATUS
DRAFT
FINALIZE
EXPORT
SYNC
REPORT
PLANNING
VALIDATE
PAY
GEN_PDF
```

Inventory actions:

```text
ENTREE_STOCK
SORTIE_STOCK
AJUSTER_STOCK
ASSIGN_EMPLACEMENT
RESERVER_STOCK
LIBERER_STOCK
CHECK_STOCK
TRANSFERER_STOCK
```

Important files:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/Action.java
osm-ms-fe/src/app/theme/types/permissions.ts
osm-prod/src/main/resources/db/migration/insert Permissions.sql
```

If you add an action, update all three places.

### Permission

A permission is one allowed action on one entity in one module.

Backend model:

```text
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/Permission.java
```

Fields:

```text
module          OSMModule
entity          String
permissionName  String
```

Example row:

```text
module = CONDITIONING
entity = OF
permissionName = START
```

Runtime authority string:

```text
CONDITIONING:OF:START
```

### Role

A role is a named set of permissions.

Backend model:

```text
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/Role.java
```

Main fields:

```text
roleName
description
permissions
```

The join table is:

```text
role_permissions
```

Users do not receive permissions directly. They receive a role, and the role
contains permissions.

### User

A user has one role.

Backend model:

```text
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/OSMUser.java
```

`OSMUser.getAuthorities()` converts role permissions into Spring authorities:

```java
String.format(
    "%s:%s:%s",
    permission.getModule().toString().toUpperCase(),
    permission.getEntity().toUpperCase(),
    permission.getPermissionName().toUpperCase()
)
```

So a role permission becomes:

```text
INVENTAIR:STOCKSEC:ENTREE_STOCK
```

## JWT Claims

When the security service issues an access token, it adds:

```text
osmUser
role
authorities
```

Important file:

```text
osm-sec/src/main/java/com/osm/securityservice/securityConfig/SecurityConfig.java
```

The relevant token customization:

```java
.claim("role", user.getRole().getRoleName())
.claim("authorities", user.getAuthorities().stream()
    .map(GrantedAuthority::getAuthority)
    .toList())
```

Example decoded token shape:

```json
{
  "role": "USER",
  "authorities": [
    "CONDITIONING:OF:READ",
    "CONDITIONING:OF:START",
    "INVENTAIR:STOCKSEC:READ",
    "INVENTAIR:STOCKSEC:ENTREE_STOCK"
  ],
  "osmUser": {
    "username": "operator1"
  }
}
```

## Permission Seed SQL

Permissions are seeded from JSON in:

```text
osm-prod/src/main/resources/db/migration/insert Permissions.sql
```

The seed function reads:

```text
spec.entities
spec.security_entities
```

Each entity entry contains:

```json
{
  "OF": {
    "description": "Conditioning manufacturing orders",
    "module": "CONDITIONING",
    "permissions": ["READ", "CREATE", "UPDATE", "DELETE", "START", "PAUSE"]
  }
}
```

The SQL creates one `permission` row per action. It is idempotent because of:

```text
uq_permission_mod_entity_name on (module, entity, permission_name)
```

To add a new entity to permissions:

1. Add the entity under `entities` or `security_entities`.
2. Set its `module`.
3. List every action that can ever be assigned to a role.
4. Make sure every action exists in backend `Action.java`.
5. Make sure the module exists in backend `OSMModule.java`.
6. Add frontend enum and translations.

## Backend Entity Action Attachment

Every DTO extends:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/dtos/BaseDto.java
```

`BaseDto` contains:

```java
private Set<Action> actions = Collections.emptySet();
```

The `actions` field is what the frontend uses to decide which buttons/actions
to show for an entity row or detail view.

### Available actions per entity state

Each service can define which actions are available for a specific entity state:

```java
public Set<Action> actionsMapping(Entity entity) {
    return Set.of(Action.READ, Action.UPDATE, Action.DELETE);
}
```

Default implementation:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/services/BaseService.java
```

Default actions:

```text
READ
CREATE
UPDATE
DELETE
```

Examples of custom mappings:

```text
osm-prod/src/main/java/com/osm/oilproductionservice/service/UnifiedDeliveryService.java
osm-cond/src/main/java/com/osm/conditioning/service/OFService.java
osm-cond/src/main/java/com/osm/conditioning/expedition/service/ExpeditionService.java
osm-cond/src/main/java/com/osm/conditioning/shipping/service/ShippingInfoService.java
osm-pack/src/main/java/com/osm/inventory_service/service/StockSecService.java
osm-pack/src/main/java/com/osm/inventory_service/service/ArticleSecService.java
```

`actionsMapping` should express business availability, not user authorization.

Example:

```text
An OF in DRAFT may allow START.
An OF already CLOSED should not allow START.
```

### Permitted actions for the connected user

The base controller filters available entity actions by the connected user's
authorities.

Important file:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/controllers/impl/BaseControllerImpl.java
```

The flow:

1. Controller defines the protected resource with `getResourceName()`.
2. Base controller reads JWT authorities from `SecurityContextHolder`.
3. It keeps only authorities matching `:<RESOURCE>:`.
4. It calls `baseService.actionsMapping(entity)` to get available actions.
5. It returns the intersection:

```text
actionsMapping(entity) INTERSECT user permissions for that entity
```

Admin roles:

```text
ADMIN
OSMADMIN
```

These roles receive all actions returned by `actionsMapping(entity)`.

Normal users only receive actions they have in their role permissions.

Example:

```text
User authorities:
  CONDITIONING:OF:READ
  CONDITIONING:OF:START

OFService.actionsMapping(of):
  READ, UPDATE, START, PAUSE, CLOSE

DTO.actions returned:
  READ, START
```

### Fetch paths that attach actions

The base controller attaches actions for:

```text
findDtoByUuid
fetchAll
fetchAllPageable
advancedSearch
create response
update response
```

Custom controller methods must call:

```java
attachPermittedActions(dto)
attachPermittedActions(list)
```

For DTOs controlled by a different resource name, use:

```java
attachPermittedActions(dto, "MOUVEMENTSTOCKSEC", Set.of(Action.READ, Action.CREATE))
```

This was added for custom endpoints in:

```text
Conditioning:
  OF
  PROJET
  CLIENT
  CERTIFICATION
  SHIPPING
  EXPEDITION
  QUALITY

Inventory:
  ARTICLESEC
  STOCKSEC
  MOUVEMENTSTOCKSEC
  PRODUITFINAL
  BOM
  BONCOMMANDE
  FOURNISSEUR
  LIGNECONDITIONNEMENT
  EMPLACEMENTSTOCK

Production:
  UNIFIEDDELIVERY custom fetch endpoints
```

## Backend Controller Rules

Every secured controller should implement:

```java
@Override
protected String getResourceName() {
    return "OF";
}
```

The return value must match the permission entity:

```text
SQL entity key
Permission.entity
JWT authority resource segment
Frontend entity enum value
```

Good examples:

```java
return "OF";
return "EXPEDITION";
return "STOCKSEC";
return "UNIFIEDDELIVERY";
```

Avoid inconsistent names such as:

```text
StockSec
stocksec
stock_sec
```

Uppercase names are safest.

## Frontend Permission Flow

### Token decoding

Frontend authentication decodes the JWT and stores:

```text
role
permissions = decodedToken.authorities
osmUser
```

Important file:

```text
osm-ms-fe/src/app/auth/services/authentication.service.ts
```

The frontend expects permissions in this exact shape:

```text
MODULE:ENTITY:ACTION
```

### Permission enums and key helper

Frontend permission constants live in:

```text
osm-ms-fe/src/app/theme/types/permissions.ts
```

Use the helper:

```ts
permissionKey(OSMModule.CONDITIONING, ConditioningEntity.OF, Action.READ)
```

This produces:

```text
CONDITIONING:OF:READ
```

Do not hand-type permission strings in routes or menus unless there is no
alternative. Using the helper prevents typos.

### Route guards

Important file:

```text
osm-ms-fe/src/app/interceptors/guards/permission.guard.ts
```

Available guards:

```ts
allPermissionGuard([...])
anyPermissionGuard([...])
moduleGuard([...])
```

Examples:

```ts
canActivate: [
  allPermissionGuard([
    permissionKey(OSMModule.CONDITIONING, ConditioningEntity.OF, Action.READ)
  ])
]
```

```ts
canActivate: [
  anyPermissionGuard([
    permissionKey(OSMModule.INVENTAIR, InventoryEntity.STOCKSEC, Action.READ),
    permissionKey(OSMModule.INVENTAIR, InventoryEntity.ARTICLESEC, Action.READ)
  ])
]
```

If the user does not have the required permission, the guard redirects to:

```text
/access-denied
```

### Menu filtering

Menu entries declare permissions in:

```text
osm-ms-fe/src/app/shared/osm_menu.ts
```

The admin layout filters menu items using the current user's permission list:

```text
osm-ms-fe/src/app/theme/layouts/admin/admin.component.ts
```

Example menu permission:

```ts
permissions: [
  permissionKey(OSMModule.CONDITIONING, ConditioningEntity.EXPEDITION, Action.READ)
]
```

### Entity row actions

The shared dashboard reads `record.actions` from the backend DTO:

```text
osm-ms-fe/src/app/shared/modules/osm-dashboard/osm-dashboard.html
osm-ms-fe/src/app/shared/modules/osm-dashboard/osm-dashboard.ts
```

The backend response controls which row actions are visible.

Example backend DTO:

```json
{
  "id": "....",
  "code": "OF-0001",
  "actions": ["READ", "START", "UPDATE"]
}
```

The frontend displays labels using:

```text
OSM_DASHBOARD.ACTIONS.<ACTION>
```

### Role permission tree

The role screen shows the permissions tree and translates every permission node:

```text
osm-ms-fe/src/app/settings/user-management/components/permission-component/permission.component.html
```

Translation key:

```text
OSM_DASHBOARD.ACTIONS.<PERMISSION_OR_ENTITY_NAME>
```

Translation files:

```text
osm-ms-fe/src/assets/i18n/fr.json
osm-ms-fe/src/assets/i18n/en.json
osm-ms-fe/src/assets/i18n/ar.json
```

If the UI shows raw text like:

```text
OSM_DASHBOARD.ACTIONS.CONDITIONING
```

then the translation key is missing under `OSM_DASHBOARD.ACTIONS`.

## Adding a New Module

Example: adding `TRACEABILITY`.

Backend:

1. Add to `OSMModule.java` in `xdev-base`.
2. Add to `OSMModule.java` in `comunicator`.
3. Add SQL mapping in `insert Permissions.sql`.
4. Add permissions under the seed JSON.

Frontend:

1. Add to `OSMModule` in `permissions.ts`.
2. Add menu/route guards using `permissionKey`.
3. Add translations under `OSM_DASHBOARD.ACTIONS`.

Important: the SQL enum ordinal must stay aligned with Java.

## Adding a New Entity

Example: adding `PACKAGINGBATCH` under `CONDITIONING`.

Backend checklist:

1. Add SQL permissions:

```json
"PACKAGINGBATCH": {
  "description": "Conditioning packaging batches",
  "module": "CONDITIONING",
  "permissions": ["READ", "CREATE", "UPDATE", "DELETE", "START", "CLOSE"]
}
```

2. Make sure each action exists in:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/Action.java
```

3. In the controller:

```java
@Override
protected String getResourceName() {
    return "PACKAGINGBATCH";
}
```

4. If the entity has state-specific actions, override:

```java
@Override
public Set<Action> actionsMapping(PackagingBatch entity) {
    Set<Action> actions = new HashSet<>(Set.of(Action.READ, Action.UPDATE));
    if (entity.canStart()) {
        actions.add(Action.START);
    }
    if (entity.canClose()) {
        actions.add(Action.CLOSE);
    }
    return actions;
}
```

5. If the controller has custom endpoints returning DTOs, call:

```java
return ResponseEntity.ok(attachPermittedActions(dto));
return ResponseEntity.ok(attachPermittedActions(list));
```

Frontend checklist:

1. Add the entity to the correct enum in:

```text
osm-ms-fe/src/app/theme/types/permissions.ts
```

2. Add route guards:

```ts
permissionKey(OSMModule.CONDITIONING, ConditioningEntity.PACKAGINGBATCH, Action.READ)
```

3. Add menu permissions in:

```text
osm-ms-fe/src/app/shared/osm_menu.ts
```

4. Add translations:

```json
"PACKAGINGBATCH": "Packaging Batch",
"START": "Start",
"CLOSE": "Close"
```

## Adding a New Action

Example: adding `ARCHIVE`.

Backend:

1. Add to:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/Action.java
```

2. Add to SQL seed for each entity that can use it:

```json
"permissions": ["READ", "ARCHIVE"]
```

3. Add it to `actionsMapping(entity)` only when the entity state allows it.

Frontend:

1. Add to:

```text
osm-ms-fe/src/app/theme/types/permissions.ts
```

2. Add translations:

```text
OSM_DASHBOARD.ACTIONS.ARCHIVE
```

3. Add an icon if the shared dashboard should display a specific icon:

```text
osm-ms-fe/src/app/shared/modules/osm-dashboard/models/actions.ts
```

4. Use it in routes, buttons, or menus only through `permissionKey`.

## Security Notes

Frontend guards and hidden buttons improve UX, but they are not a security
boundary. The backend must remain the source of truth.

Current backend action attachment answers:

```text
"What actions should this connected user see for this fetched entity?"
```

It does not automatically block every mutation endpoint. If an endpoint must be
strictly protected, also enforce it with Spring Security rules, method-level
authorization, or explicit permission checks.

Recommended future hardening:

```java
@PreAuthorize("hasAuthority('CONDITIONING:OF:START')")
```

or a shared helper that checks:

```text
current user has MODULE:ENTITY:ACTION
```

before executing business logic.

## Troubleshooting

### User sees a route/menu item missing

Check:

1. JWT contains the expected authority.
2. Frontend route/menu uses the same `MODULE:ENTITY:ACTION`.
3. `permissionKey(...)` uses the correct module/entity enum.
4. User role has the permission in the role screen.

### Entity row has empty `actions`

Check:

1. Controller `getResourceName()` matches the permission entity.
2. User JWT has at least one authority for that entity.
3. Service `actionsMapping(entity)` returns that action.
4. The endpoint calls `attachPermittedActions(...)`.
5. The DTO extends `BaseDto`.

### Admin sees actions but normal user does not

This usually means the entity state mapping is correct, but the normal user's
role does not include the matching permission.

Example:

```text
DTO action missing: START
Needed authority: CONDITIONING:OF:START
```

### Permission tree shows raw translation keys

Add missing labels under:

```text
OSM_DASHBOARD.ACTIONS
```

in:

```text
fr.json
en.json
ar.json
```

### New permission does not appear in role management

Check:

1. It exists in `insert Permissions.sql`.
2. The migration ran against the current database.
3. The `(module, entity, permission_name)` combination is unique.
4. Module string maps to an `OSMModule` ordinal in the seed function.

### Backend compile fails locally

The current project dependencies require a newer Java toolchain. If compile
fails with:

```text
release version 21 not supported
class file has wrong version
```

install/use JDK 21 and rerun Maven with `JAVA_HOME` pointing to JDK 21.

If `osm-prod` fails with GitHub Maven `401 Unauthorized`, configure credentials
for the private GitHub package repository.

## Reference Files

Security service:

```text
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/OSMUser.java
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/Role.java
osm-sec/src/main/java/com/osm/securityservice/userManagement/models/Permission.java
osm-sec/src/main/java/com/osm/securityservice/securityConfig/SecurityConfig.java
```

Shared backend:

```text
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/Action.java
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/models/OSMModule.java
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/dtos/BaseDto.java
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/services/BaseService.java
osm-parent/xdev-base/src/main/java/com/xdev/xdevbase/controllers/impl/BaseControllerImpl.java
```

Permission seed:

```text
osm-prod/src/main/resources/db/migration/insert Permissions.sql
```

Frontend:

```text
osm-ms-fe/src/app/theme/types/permissions.ts
osm-ms-fe/src/app/auth/services/authentication.service.ts
osm-ms-fe/src/app/interceptors/guards/permission.guard.ts
osm-ms-fe/src/app/shared/osm_menu.ts
osm-ms-fe/src/app/shared/modules/osm-dashboard/osm-dashboard.html
osm-ms-fe/src/app/settings/user-management/components/permission-component/permission.component.html
osm-ms-fe/src/assets/i18n/fr.json
osm-ms-fe/src/assets/i18n/en.json
osm-ms-fe/src/assets/i18n/ar.json
```
