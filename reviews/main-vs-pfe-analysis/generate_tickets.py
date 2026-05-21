import os

tickets = {
    "TICKET-001": """# TICKET-001: Backend - Atomicité de la Création d'Utilisateur et des Emails

**Priority:** High / Critical  
**Component:** `osm-sec` (`UserService.java`)

## 📝 The Problem
When creating a user or resetting a password, the system persists the user state in the database and then sends an email. If the email delivery fails (e.g., SMTP server down), the transaction is not rolled back. This leaves "ghost" users in the database who cannot log in and cannot register again.

## 🛠 Technical Cause
Spring's `@Transactional` annotation only rolls back on `RuntimeException` by default. The `MailServiceImpl.sendEmail()` method throws a `MessagingException` (which is a checked exception). Because of this, the transaction commits the database insert before the email fails. Additionally, `resetPassword` lacks `@Transactional` entirely.

## 🚀 Explicit Fix (Step-by-Step)
1. **Update Annotations:** Modify `UserService.java` to explicitly roll back on any Exception.
2. **Add Transactional to Reset Password:** Protect the reset flow.

**Code Example (`UserService.java`):**
```java
// Fix 1: Add rollbackFor
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> addUser(@RequestBody SignupRequest signUpRequest) throws MessagingException {
    // ... existing logic ...
    mailService.sendEmail(user.getEmail(), "Activation", content);
}

// Fix 2: Protect Reset Password
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> resetPassword(@RequestBody ResetPasswordRequest request) throws MessagingException {
    // ... existing logic ...
}
```

## ✅ Acceptance Criteria
* Throwing a mock `MessagingException` during user creation successfully rolls back the database insert.
* `resetPassword` is fully transactional.
""",
    "TICKET-002": """# TICKET-002: Frontend - Abstraction des URLs API (Environnement)

**Priority:** High  
**Component:** `osm-ms-fe` (Angular)

## 📝 The Problem
Several core services in the frontend use hardcoded URLs like `http://localhost:8084`. This breaks the app entirely when deployed to a production environment.

## 🛠 Technical Cause
Because `proxy.conf.json` was deleted in the `pfe` branch, developers bypassed CORS locally by hardcoding absolute URLs in services like `BomService.ts`, `QualityService.ts`, `sku.service.ts`, etc.

## 🚀 Explicit Fix (Step-by-Step)
1. Inject the `environment` configuration into the services.
2. Replace hardcoded strings with `environment.apiUrl`.

**Code Example (`BomService.ts`):**
```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BomService {
    // ❌ REMOVE THIS:
    // private apiUrl = 'http://localhost:8084/api/inventaire/boms';
    
    // ✅ USE THIS:
    private apiUrl = `${environment.apiUrl}/api/inventaire/boms`;

    constructor(private http: HttpClient) {}
}
```

## ✅ Acceptance Criteria
* No occurrences of `localhost` remain in the `src/app` directory.
* The application compiles and routes API calls dynamically based on `environment.ts` and `environment.prod.ts`.
""",
    "TICKET-003": """# TICKET-003: Mobile - Correction de l'IP de l'Émulateur

**Priority:** High  
**Component:** `osm-mobile` (Android)

## 📝 The Problem
The Android application uses hardcoded IP addresses (`http://10.0.2.2` or `192.168.0.254`) for backend communication. This prevents building a single APK that works in production or on physical devices without recompiling.

## 🛠 Technical Cause
The `Constants.kt` file defines `BASE_URL` as a static constant string.

## 🚀 Explicit Fix (Step-by-Step)
1. **Remove Hardcoded IP:** Delete `BASE_URL` from `Constants.kt`.
2. **Use BuildConfig:** Add `buildConfigField` in `build.gradle` (app level) for different flavors.

**Code Example (`build.gradle`):**
```groovy
android {
    buildTypes {
        debug {
            buildConfigField "String", "BASE_URL", "\\"http://192.168.0.254:8084/\\""
        }
        release {
            buildConfigField "String", "BASE_URL", "\\"https://api.osm-production.com/\\""
        }
    }
}
```

**Code Example (`RetrofitClient.kt`):**
```kotlin
Retrofit.Builder()
    // ✅ Use BuildConfig instead of Constants
    .baseUrl(BuildConfig.BASE_URL)
    .client(client)
```

## ✅ Acceptance Criteria
* Physical devices can hit the API by simply switching build variants.
* `Constants.kt` no longer holds IP addresses.
""",
    "TICKET-004": """# TICKET-004: Backend - Anti-pattern de Gestion des Exceptions (RuntimeException)

**Priority:** Medium  
**Component:** `osm-prod`, `osm-pack`

## 📝 The Problem
Domain exceptions are swallowed and wrapped in generic `RuntimeException`s. This forces the frontend to deal with generic 500 Internal Server Errors instead of clean 400 or 404 responses.

## 🛠 Technical Cause
Controllers (like `BomController.java`) use manual `try/catch` blocks returning `ResponseEntity.status(HttpStatus.BAD_REQUEST)`. Services (like `FiltrationService.java`) catch all exceptions and do `throw new RuntimeException("...", e)`.

## 🚀 Explicit Fix (Step-by-Step)
1. **Create Custom Exceptions:** E.g., `ResourceNotFoundException`.
2. **Implement @ControllerAdvice:** Handle them globally.

**Code Example (`GlobalExceptionHandler.java` in `osm-pack`):**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<?> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", ex.getMessage()));
    }
}
```

**Code Example (`BomController.java`):**
```java
// ❌ REMOVE manual try/catch:
@GetMapping("/{id}")
public ResponseEntity<?> getBomById(@PathVariable UUID id) {
    // ✅ JUST RETURN THE DTO. Let ControllerAdvice handle the errors.
    return ResponseEntity.ok(bomService.getBomById(id));
}
```

## ✅ Acceptance Criteria
* Controllers no longer have manual `try/catch` for domain logic.
* HTTP 404 is correctly returned when a resource is missing.
""",
    "TICKET-005": """# TICKET-005: Architecture - Duplication des DTOs (Split-Brain)

**Priority:** High  
**Component:** All Backend Microservices (`osm-parent`, `osm-pack`, `osm-prod`)

## 📝 The Problem
Data Transfer Objects (DTOs) like `StorageUnitDto` are copy-pasted across different microservices. When `osm-prod` sends a Feign request to `osm-pack`, it relies on a duplicated DTO class, which causes serialization bugs when the schemas drift.

## 🛠 Technical Cause
Lack of a shared library for external API contracts.

## 🚀 Explicit Fix (Step-by-Step)
1. **Create Shared Module:** Inside `osm-parent`, create a new maven module `osm-shared-dto`.
2. **Migrate DTOs:** Move classes like `BonCommandeDto`, `StorageUnitDto` to this module.
3. **Update Dependencies:** Add `<dependency><groupId>com.osm</groupId><artifactId>osm-shared-dto</artifactId></dependency>` to the microservices.
4. **Refactor Imports:** Change the package imports in controllers and Feign clients.

## ✅ Acceptance Criteria
* `StorageUnitDto.java` exists only once in the entire repository (`osm-shared-dto`).
* All microservices compile successfully using the shared dependency.
""",
    "TICKET-006": """# TICKET-006: Frontend - Correction du Port Backend (StatistiqueService)

**Priority:** High  
**Component:** `osm-ms-fe`

## 📝 The Problem
The Stock statistics pages fail to load data because the frontend requests are sent to port `8080` instead of the Gateway port `8084`.

## 🛠 Technical Cause
In `statistique.service.ts`, the URL is hardcoded as `http://localhost:8080/api/statistiques`.

## 🚀 Explicit Fix (Step-by-Step)
1. This will be fixed alongside TICKET-002, but specifically requires ensuring the route matches the Gateway configuration.

**Code Example (`statistique.service.ts`):**
```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatistiqueService {
    // ✅ Change port and use environment
    private apiUrl = `${environment.apiUrl}/api/statistiques`;
}
```

## ✅ Acceptance Criteria
* Statistics charts and data load correctly without CORS or Network connection errors.
""",
    "TICKET-007": """# TICKET-007: Architecture - Standardization des Entités et Validations

**Priority:** Medium  
**Component:** Backend

## 📝 The Problem
Inconsistent entity validation and lack of standard auditing fields (created_at, updated_at).

## 🛠 Technical Cause
Some new entities in `osm-pack` and `osm-prod` do not extend a `BaseEntity` or use `@EntityListeners(AuditingEntityListener.class)`.

## 🚀 Explicit Fix (Step-by-Step)
1. Ensure all new JPA entities inherit from `BaseEntity` (from `osm-parent`).
2. Add `@Valid` to Controller request bodies.

## ✅ Acceptance Criteria
* All entities have automatic auditing timestamps.
""",
    "TICKET-008": """# TICKET-008: Frontend - Restauration du Tableau de Bord (Dashboard)

**Priority:** High  
**Component:** `osm-ms-fe`

## 📝 The Problem
The main Stock Dashboard (`http://localhost:4200/stock/dashboard`) returns a 404. The entire file is commented out in the codebase.

## 🛠 Technical Cause
`stock-dashboard.component.ts` logic is entirely wrapped in `/* ... */`, likely due to unresolved compilation errors from Chart.js updates during the `pfe` branch merge.

## 🚀 Explicit Fix (Step-by-Step)
1. **Uncomment Code:** Remove the `/* */` block in `stock-dashboard.component.ts`.
2. **Fix Imports:** Update the Chart.js or ng2-charts imports to match the current `package.json` version.
3. **Restore Routing:** Ensure `stock-routing.module.ts` has `{ path: 'dashboard', component: StockDashboardComponent }` uncommented.

## ✅ Acceptance Criteria
* Navigating to the Stock module shows the dashboard by default.
* Charts render without console compilation errors.
""",
    "TICKET-009": """# TICKET-009: Frontend - Fuites de Mémoire Angular (Memory Leaks)

**Priority:** Medium  
**Component:** `osm-ms-fe`

## 📝 The Problem
The UI will slow down over time as users navigate through pages, eventually crashing the browser tab.

## 🛠 Technical Cause
Components like `ArticleListComponent` use `.subscribe()` to API observables but do not implement `ngOnDestroy` to clean them up, creating RxJS memory leaks.

## 🚀 Explicit Fix (Step-by-Step)
1. Implement `OnDestroy` in the components.
2. Use a `Subject` and the `takeUntil` operator.

**Code Example (`ArticleListComponent.ts`):**
```typescript
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

export class ArticleListComponent implements OnInit, OnDestroy {
    private destroy$ = new Subject<void>();

    loadArticles() {
        this.articleService.getArticles()
            .pipe(takeUntil(this.destroy$)) // ✅ ADD THIS
            .subscribe(data => this.articles = data);
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete(); // ✅ CLEANUP
    }
}
```

## ✅ Acceptance Criteria
* All infinite or long-lived subscriptions are properly terminated on component destruction.
""",
    "TICKET-010": """# TICKET-010: Sécurité - Manque de Contrôle d'Accès (RBAC)

**Priority:** Critical  
**Component:** Frontend & Backend (`osm-pack`, `osm-prod`, `osm-ms-fe`)

## 📝 The Problem
Any logged-in user can access Stock management screens and trigger Backend API endpoints to modify production data.

## 🛠 Technical Cause
* Frontend: Missing `canActivate: [anyPermissionGuard]` in `stock-routing.module.ts`.
* Backend: Missing `@PreAuthorize` in controllers like `BomController.java`.

## 🚀 Explicit Fix (Step-by-Step)

**Frontend Fix (`stock-routing.module.ts`):**
```typescript
{
    path: 'articles',
    component: ArticleListComponent,
    // ✅ Add Guard
    canActivate: [anyPermissionGuard([permissionKey(OSMModule.STOCK, StockEntity.ARTICLE, Action.READ)])]
}
```

**Backend Fix (`BomController.java`):**
```java
@PostMapping("/create")
// ✅ Add Spring Security Annotation
@PreAuthorize("hasAuthority('STOCK:BOM:CREATE')")
public ResponseEntity<?> createBom(@RequestBody BOMDto bomDto) { ... }
```

## ✅ Acceptance Criteria
* Users without Stock permissions cannot navigate to the UI routes.
* API returns 403 Forbidden for unauthorized backend calls.
""",
    "TICKET-011": """# TICKET-011: Qualité - Standardisation de la Journalisation (Logging)

**Priority:** Low  
**Component:** Frontend & Backend

## 📝 The Problem
Logs are a mess. Backend uses blocking `System.out.println`. Frontend leaves `console.log` in production, exposing sensitive variables to users.

## 🛠 Technical Cause
Developers ignored the existing `OSMLogger` utility and used native console printing.

## 🚀 Explicit Fix (Step-by-Step)
1. **Backend:** Replace `System.out.println("Alerte: " + ...)` with `OSMLogger.logMethodEntry(this.getClass(), "checkSeuils", "Alerte...");`
2. **Frontend:** Remove `console.log` from `view-oil-transaction.component.ts` and `default.component.ts`. Configure Angular CLI to strip logs in production `angular.json` optimization config.

## ✅ Acceptance Criteria
* Zero occurrences of `System.out.println` or `e.printStackTrace()` in backend Java code.
""",
    "TICKET-012": """# TICKET-012: Frontend - Standardisation UI/UX et Responsivité

**Priority:** Medium  
**Component:** `osm-ms-fe`

## 📝 The Problem
The frontend UI is not responsive on mobile. Tables have no pagination and will crash with large datasets. Huge chunks of SCSS are duplicated across files.

## 🛠 Technical Cause
`*ngFor` is used without paginators. CSS `grid-template-columns` is used without media queries. Over 250 lines of SCSS are duplicated per component.

## 🚀 Explicit Fix (Step-by-Step)
1. **Extract SCSS:** Move the `.filters-card`, `.page-header`, and `.table-card` classes into `src/styles.scss`.
2. **Add Bootstrap Grids:** Change `<div class="filters-grid">` to `<div class="row">` and wrap inputs in `<div class="col-12 col-md-4">`.
3. **Add Pagination:** Install/Use `<mat-paginator>` or ng-bootstrap pagination for the tables.

## ✅ Acceptance Criteria
* Deleting SCSS from individual components does not break the layout.
* UI collapses gracefully on mobile devices.
""",
    "TICKET-013": """# TICKET-013: Mobile - Vulnérabilités de Sécurité Critiques

**Priority:** Critical  
**Component:** `osm-mobile`

## 📝 The Problem
The mobile app stores the OAuth `CLIENT_SECRET` and `QR_SECRET` in plain text. JWT tokens are saved unencrypted, and network traffic prints passwords to the device logcat.

## 🛠 Technical Cause
`Constants.kt` holds secrets. `SessionManager.kt` uses legacy `SharedPreferences`. `RetrofitClient.kt` uses `HttpLoggingInterceptor.Level.BODY`.

## 🚀 Explicit Fix (Step-by-Step)
1. **Remove Body Logging (`RetrofitClient.kt`):**
```kotlin
private val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
}
```

2. **Encrypt SharedPreferences (`SessionManager.kt`):**
```kotlin
// ✅ Use EncryptedSharedPreferences
val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
val prefs = EncryptedSharedPreferences.create(
    Constants.PREF_NAME, masterKeyAlias, context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

## ✅ Acceptance Criteria
* `CLIENT_SECRET` is completely removed from source control (moved to `local.properties`).
* Tokens are securely encrypted on disk.
""",
    "TICKET-014": """# TICKET-014: Mobile - Dette Architecturale (MVVM) et UI

**Priority:** Medium  
**Component:** `osm-mobile`

## 📝 The Problem
The mobile codebase is an unmaintainable "Spaghetti" structure where Activities handle networking, databases, and UI concurrently. UI text is hardcoded, preventing translation.

## 🛠 Technical Cause
`MainActivity.kt` bypasses the ViewModel architecture. Hardcoded `android:text="Orders (OF)"` in `activity_main.xml`.

## 🚀 Explicit Fix (Step-by-Step)
1. **Create ViewModels:** Move `offlineManager.syncPendingScans()` into a `MainViewModel.kt` class.
2. **Extract Strings:** 
In `res/values/strings.xml`:
```xml
<string name="card_orders">Commandes (OF)</string>
```
In `activity_main.xml`:
```xml
android:text="@string/card_orders"
```

## ✅ Acceptance Criteria
* `MainActivity.kt` only observes LiveData/StateFlow and handles UI clicks.
* All hardcoded text strings are replaced with `@string/` references.
"""
}

# Ensure the directory exists
out_dir = r"f:\OSM PROJECT\reviews\main-vs-pfe-analysis\jira-tickets"
os.makedirs(out_dir, exist_ok=True)

for ticket_id, content in tickets.items():
    file_path = os.path.join(out_dir, f"{ticket_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(tickets)} markdown files in {out_dir}.")
