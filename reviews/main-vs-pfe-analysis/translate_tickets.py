import os

tickets_fr = {
    "TICKET-001": """# TICKET-001 : Backend - Atomicité de la Création d'Utilisateur et des Emails

**Priorité :** Haute / Critique  
**Composant :** `osm-sec` (`UserService.java`)

## 📝 Le Problème
Lors de la création d'un utilisateur ou de la réinitialisation d'un mot de passe, le système enregistre l'état de l'utilisateur en base de données puis envoie un e-mail. Si l'envoi de l'e-mail échoue (ex: serveur SMTP indisponible), la transaction n'est pas annulée (rollback). Cela laisse des utilisateurs "fantômes" en base qui ne peuvent pas se connecter et ne peuvent pas s'inscrire à nouveau.

## 🛠 Cause Technique
L'annotation `@Transactional` de Spring n'annule la transaction que sur les `RuntimeException` par défaut. La méthode `MailServiceImpl.sendEmail()` lève une `MessagingException` (qui est une exception contrôlée / checked). De ce fait, la transaction valide l'insertion en base avant que l'e-mail n'échoue. De plus, `resetPassword` manque totalement de l'annotation `@Transactional`.

## 🚀 Correction Explicite (Étape par étape)
1. **Mettre à jour les annotations :** Modifier `UserService.java` pour annuler explicitement sur toute Exception.
2. **Ajouter @Transactional à Reset Password :** Protéger le flux de réinitialisation.

**Exemple de Code (`UserService.java`) :**
```java
// Correctif 1 : Ajouter rollbackFor
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> addUser(@RequestBody SignupRequest signUpRequest) throws MessagingException {
    // ... logique existante ...
    mailService.sendEmail(user.getEmail(), "Activation", content);
}

// Correctif 2 : Protéger Reset Password
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> resetPassword(@RequestBody ResetPasswordRequest request) throws MessagingException {
    // ... logique existante ...
}
```

## ✅ Critères d'Acceptation
* Lever une fausse `MessagingException` pendant la création d'un utilisateur annule correctement l'insertion en base.
* `resetPassword` est entièrement transactionnel.
""",
    "TICKET-002": """# TICKET-002 : Frontend - Abstraction des URLs API (Environnement)

**Priorité :** Haute  
**Composant :** `osm-ms-fe` (Angular)

## 📝 Le Problème
Plusieurs services clés du frontend utilisent des URLs codées en dur comme `http://localhost:8084`. Cela rend l'application inutilisable dès qu'elle est déployée dans un environnement de production.

## 🛠 Cause Technique
Comme le fichier `proxy.conf.json` a été supprimé dans la branche `pfe`, les développeurs ont contourné les erreurs CORS localement en codant en dur les URLs absolues dans les services comme `BomService.ts`, `QualityService.ts`, `sku.service.ts`, etc.

## 🚀 Correction Explicite (Étape par étape)
1. Injecter la configuration `environment` dans les services.
2. Remplacer les chaînes en dur par `environment.apiUrl`.

**Exemple de Code (`BomService.ts`) :**
```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class BomService {
    // ❌ SUPPRIMER CECI :
    // private apiUrl = 'http://localhost:8084/api/inventaire/boms';
    
    // ✅ UTILISER CECI :
    private apiUrl = `${environment.apiUrl}/api/inventaire/boms`;

    constructor(private http: HttpClient) {}
}
```

## ✅ Critères d'Acceptation
* Plus aucune occurrence de `localhost` ne reste dans le répertoire `src/app`.
* L'application compile et redirige les appels API dynamiquement en fonction de `environment.ts` et `environment.prod.ts`.
""",
    "TICKET-003": """# TICKET-003 : Mobile - Correction de l'IP de l'Émulateur

**Priorité :** Haute  
**Composant :** `osm-mobile` (Android)

## 📝 Le Problème
L'application Android utilise des adresses IP codées en dur (`http://10.0.2.2` ou `192.168.0.254`) pour la communication avec le backend. Cela empêche de générer un seul APK qui fonctionne en production ou sur des appareils physiques sans recompiler.

## 🛠 Cause Technique
Le fichier `Constants.kt` définit `BASE_URL` comme une constante statique de type String.

## 🚀 Correction Explicite (Étape par étape)
1. **Supprimer l'IP en dur :** Supprimer `BASE_URL` de `Constants.kt`.
2. **Utiliser BuildConfig :** Ajouter `buildConfigField` dans `build.gradle` (niveau app) pour différents flavors.

**Exemple de Code (`build.gradle`) :**
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

**Exemple de Code (`RetrofitClient.kt`) :**
```kotlin
Retrofit.Builder()
    // ✅ Utiliser BuildConfig au lieu de Constants
    .baseUrl(BuildConfig.BASE_URL)
    .client(client)
```

## ✅ Critères d'Acceptation
* Les appareils physiques peuvent contacter l'API simplement en changeant de build variant.
* `Constants.kt` ne contient plus d'adresses IP.
""",
    "TICKET-004": """# TICKET-004 : Backend - Anti-pattern de Gestion des Exceptions (RuntimeException)

**Priorité :** Moyenne  
**Composant :** `osm-prod`, `osm-pack`

## 📝 Le Problème
Les exceptions du domaine sont interceptées et encapsulées dans des `RuntimeException` génériques. Cela force le frontend à gérer des erreurs 500 Internal Server Error génériques au lieu de réponses 400 ou 404 propres.

## 🛠 Cause Technique
Les contrôleurs (comme `BomController.java`) utilisent des blocs `try/catch` manuels retournant `ResponseEntity.status(HttpStatus.BAD_REQUEST)`. Les services (comme `FiltrationService.java`) interceptent toutes les exceptions et font `throw new RuntimeException("...", e)`.

## 🚀 Correction Explicite (Étape par étape)
1. **Créer des Exceptions Personnalisées :** Ex: `ResourceNotFoundException`.
2. **Implémenter @ControllerAdvice :** Les gérer globalement.

**Exemple de Code (`GlobalExceptionHandler.java` dans `osm-pack`) :**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<?> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", ex.getMessage()));
    }
}
```

**Exemple de Code (`BomController.java`) :**
```java
// ❌ SUPPRIMER le try/catch manuel :
@GetMapping("/{id}")
public ResponseEntity<?> getBomById(@PathVariable UUID id) {
    // ✅ RETOURNER DIRECTEMENT LE DTO. Laisser le ControllerAdvice gérer les erreurs.
    return ResponseEntity.ok(bomService.getBomById(id));
}
```

## ✅ Critères d'Acceptation
* Les contrôleurs n'ont plus de `try/catch` manuel pour la logique métier.
* HTTP 404 est correctement retourné quand une ressource est manquante.
""",
    "TICKET-005": """# TICKET-005 : Architecture - Duplication des DTOs (Split-Brain)

**Priorité :** Haute  
**Composant :** Tous les Microservices Backend (`osm-parent`, `osm-pack`, `osm-prod`)

## 📝 Le Problème
Les Data Transfer Objects (DTOs) comme `StorageUnitDto` sont copiés-collés dans différents microservices. Quand `osm-prod` envoie une requête Feign à `osm-pack`, il dépend d'une classe DTO dupliquée, ce qui cause des bugs de sérialisation lorsque les schémas divergent.

## 🛠 Cause Technique
Manque d'une bibliothèque partagée pour les contrats d'API externes.

## 🚀 Correction Explicite (Étape par étape)
1. **Créer un Module Partagé :** Dans `osm-parent`, créer un nouveau module maven `osm-shared-dto`.
2. **Migrer les DTOs :** Déplacer les classes comme `BonCommandeDto`, `StorageUnitDto` vers ce module.
3. **Mettre à jour les Dépendances :** Ajouter `<dependency><groupId>com.osm</groupId><artifactId>osm-shared-dto</artifactId></dependency>` aux microservices.
4. **Refactoriser les Imports :** Changer les packages d'importation dans les contrôleurs et clients Feign.

## ✅ Critères d'Acceptation
* `StorageUnitDto.java` n'existe qu'une seule fois dans tout le dépôt (`osm-shared-dto`).
* Tous les microservices compilent avec succès en utilisant la dépendance partagée.
""",
    "TICKET-006": """# TICKET-006 : Frontend - Correction du Port Backend (StatistiqueService)

**Priorité :** Haute  
**Composant :** `osm-ms-fe`

## 📝 Le Problème
Les pages de statistiques de Stock échouent à charger les données car les requêtes frontend sont envoyées au port `8080` au lieu du port de la Gateway `8084`.

## 🛠 Cause Technique
Dans `statistique.service.ts`, l'URL est codée en dur comme `http://localhost:8080/api/statistiques`.

## 🚀 Correction Explicite (Étape par étape)
1. Ceci sera corrigé en même temps que le TICKET-002, mais nécessite spécifiquement de s'assurer que la route correspond à la configuration de la Gateway.

**Exemple de Code (`statistique.service.ts`) :**
```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatistiqueService {
    // ✅ Changer le port et utiliser l'environnement
    private apiUrl = `${environment.apiUrl}/api/statistiques`;
}
```

## ✅ Critères d'Acceptation
* Les graphiques et données de statistiques se chargent correctement sans erreurs CORS ou de connexion réseau.
""",
    "TICKET-007": """# TICKET-007 : Architecture - Standardisation des Entités et Validations

**Priorité :** Moyenne  
**Composant :** Backend

## 📝 Le Problème
Validation incohérente des entités et manque de champs d'audit standards (created_at, updated_at).

## 🛠 Cause Technique
Certaines nouvelles entités dans `osm-pack` et `osm-prod` n'étendent pas `BaseEntity` ou n'utilisent pas `@EntityListeners(AuditingEntityListener.class)`.

## 🚀 Correction Explicite (Étape par étape)
1. S'assurer que toutes les nouvelles entités JPA héritent de `BaseEntity` (depuis `osm-parent`).
2. Ajouter `@Valid` aux corps des requêtes des Contrôleurs.

## ✅ Critères d'Acceptation
* Toutes les entités ont des horodatages d'audit automatiques.
""",
    "TICKET-008": """# TICKET-008 : Frontend - Restauration du Tableau de Bord (Dashboard)

**Priorité :** Haute  
**Composant :** `osm-ms-fe`

## 📝 Le Problème
Le tableau de bord principal des Stocks (`http://localhost:4200/stock/dashboard`) retourne une 404. Le fichier entier est commenté dans le code source.

## 🛠 Cause Technique
La logique de `stock-dashboard.component.ts` est entièrement enveloppée dans des `/* ... */`, probablement à cause d'erreurs de compilation non résolues lors des mises à jour de Chart.js pendant la fusion de la branche `pfe`.

## 🚀 Correction Explicite (Étape par étape)
1. **Décommenter le Code :** Supprimer le bloc `/* */` dans `stock-dashboard.component.ts`.
2. **Fixer les Imports :** Mettre à jour les imports de Chart.js ou ng2-charts pour correspondre à la version actuelle du `package.json`.
3. **Restaurer le Routage :** S'assurer que `stock-routing.module.ts` a le chemin `{ path: 'dashboard', component: StockDashboardComponent }` décommenté.

## ✅ Critères d'Acceptation
* La navigation vers le module Stock affiche le tableau de bord par défaut.
* Les graphiques s'affichent sans erreurs de compilation dans la console.
""",
    "TICKET-009": """# TICKET-009 : Frontend - Fuites de Mémoire Angular (Memory Leaks)

**Priorité :** Moyenne  
**Composant :** `osm-ms-fe`

## 📝 Le Problème
L'interface utilisateur va ralentir avec le temps quand les utilisateurs naviguent entre les pages, finissant par faire planter l'onglet du navigateur.

## 🛠 Cause Technique
Les composants comme `ArticleListComponent` utilisent `.subscribe()` sur les observables d'API mais n'implémentent pas `ngOnDestroy` pour les nettoyer, créant des fuites de mémoire RxJS.

## 🚀 Correction Explicite (Étape par étape)
1. Implémenter `OnDestroy` dans les composants.
2. Utiliser un `Subject` et l'opérateur `takeUntil`.

**Exemple de Code (`ArticleListComponent.ts`) :**
```typescript
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

export class ArticleListComponent implements OnInit, OnDestroy {
    private destroy$ = new Subject<void>();

    loadArticles() {
        this.articleService.getArticles()
            .pipe(takeUntil(this.destroy$)) // ✅ AJOUTER CECI
            .subscribe(data => this.articles = data);
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete(); // ✅ NETTOYAGE
    }
}
```

## ✅ Critères d'Acceptation
* Toutes les souscriptions infinies ou à longue durée de vie sont correctement terminées lors de la destruction du composant.
""",
    "TICKET-010": """# TICKET-010 : Sécurité - Manque de Contrôle d'Accès (RBAC)

**Priorité :** Critique  
**Composant :** Frontend & Backend (`osm-pack`, `osm-prod`, `osm-ms-fe`)

## 📝 Le Problème
N'importe quel utilisateur connecté peut accéder aux écrans de gestion du Stock et déclencher les points d'API Backend pour modifier les données de production.

## 🛠 Cause Technique
* Frontend : Manque de `canActivate: [anyPermissionGuard]` dans `stock-routing.module.ts`.
* Backend : Manque de `@PreAuthorize` dans les contrôleurs comme `BomController.java`.

## 🚀 Correction Explicite (Étape par étape)

**Correctif Frontend (`stock-routing.module.ts`) :**
```typescript
{
    path: 'articles',
    component: ArticleListComponent,
    // ✅ Ajouter le Guard
    canActivate: [anyPermissionGuard([permissionKey(OSMModule.STOCK, StockEntity.ARTICLE, Action.READ)])]
}
```

**Correctif Backend (`BomController.java`) :**
```java
@PostMapping("/create")
// ✅ Ajouter l'annotation de sécurité Spring
@PreAuthorize("hasAuthority('STOCK:BOM:CREATE')")
public ResponseEntity<?> createBom(@RequestBody BOMDto bomDto) { ... }
```

## ✅ Critères d'Acceptation
* Les utilisateurs sans permissions Stock ne peuvent pas naviguer vers les routes de l'UI.
* L'API retourne 403 Forbidden pour les appels backend non autorisés.
""",
    "TICKET-011": """# TICKET-011 : Qualité - Standardisation de la Journalisation (Logging)

**Priorité :** Basse  
**Composant :** Frontend & Backend

## 📝 Le Problème
Les logs sont désordonnés. Le Backend utilise des appels bloquants `System.out.println` et `e.printStackTrace()`. Le Frontend laisse des `console.log` en production, exposant des variables sensibles aux utilisateurs.

## 🛠 Cause Technique
Les développeurs ont ignoré l'utilitaire `LoggingUtils` existant et ont utilisé l'impression native en console.

## 🚀 Correction Explicite (Étape par étape)
1. **Backend :** Remplacer `System.out.println("Alerte: " + ...)` par `LoggingUtils.logMethodEntry(log, "checkSeuils", "Alerte...");`
2. **Gestion des erreurs Backend :** Remplacer `e.printStackTrace()` par `LoggingUtils.logError(log, "Message d'erreur", e);`
3. **Frontend :** Supprimer les `console.log` de `view-oil-transaction.component.ts` et `default.component.ts`. Configurer Angular CLI pour supprimer les logs dans la configuration d'optimisation production du `angular.json`.

## ✅ Critères d'Acceptation
* Zéro occurrence de `System.out.println` ou `e.printStackTrace()` dans le code Java backend.
* Tous les logs backend suivent le pattern `LoggingUtils`.
""",
    "TICKET-012": """# TICKET-012 : Frontend - Standardisation UI/UX et Responsivité

**Priorité :** Moyenne  
**Composant :** `osm-ms-fe`

## 📝 Le Problème
L'UI frontend n'est pas responsive sur mobile. Les tableaux n'ont pas de pagination et feront planter le navigateur avec de gros volumes de données. Des blocs entiers de SCSS sont dupliqués entre les fichiers.

## 🛠 Cause Technique
`*ngFor` est utilisé sans paginateurs. Les grilles CSS `grid-template-columns` sont utilisées sans media queries. Plus de 250 lignes de SCSS sont dupliquées par composant.

## 🚀 Correction Explicite (Étape par étape)
1. **Extraire le SCSS :** Déplacer les classes `.filters-card`, `.page-header`, et `.table-card` dans `src/styles.scss`.
2. **Ajouter les Grilles Bootstrap :** Changer `<div class="filters-grid">` en `<div class="row">` et envelopper les inputs dans des `<div class="col-12 col-md-4">`.
3. **Ajouter la Pagination :** Installer/Utiliser `<mat-paginator>` ou la pagination ng-bootstrap pour les tableaux.

## ✅ Critères d'Acceptation
* La suppression du SCSS des composants individuels ne casse pas la mise en page.
* L'UI s'adapte gracieusement sur les appareils mobiles.
""",
    "TICKET-013": """# TICKET-013 : Mobile - Vulnérabilités de Sécurité Critiques

**Priorité :** Critique  
**Composant :** `osm-mobile`

## 📝 Le Problème
L'application mobile stocke le `CLIENT_SECRET` OAuth et le `QR_SECRET` en texte clair. Les jetons JWT sont enregistrés sans chiffrement, et le trafic réseau imprime les mots de passe dans le logcat de l'appareil.

## 🛠 Cause Technique
`Constants.kt` contient les secrets. `SessionManager.kt` utilise les `SharedPreferences` classiques. `RetrofitClient.kt` utilise `HttpLoggingInterceptor.Level.BODY`.

## 🚀 Correction Explicite (Étape par étape)
1. **Supprimer le Log du Corps de Requête (`RetrofitClient.kt`) :**
```kotlin
private val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
}
```

2. **Chiffrer les SharedPreferences (`SessionManager.kt`) :**
```kotlin
// ✅ Utiliser EncryptedSharedPreferences
val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
val prefs = EncryptedSharedPreferences.create(
    Constants.PREF_NAME, masterKeyAlias, context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

## ✅ Critères d'Acceptation
* `CLIENT_SECRET` est totalement supprimé du contrôle de source (déplacé dans `local.properties`).
* Les jetons sont chiffrés de manière sécurisée sur le disque.
""",
    "TICKET-014": """# TICKET-014 : Mobile - Dette Architecturale (MVVM) et UI

**Priorité :** Moyenne  
**Composant :** `osm-mobile`

## 📝 Le Problème
Le code mobile est une structure "Spaghetti" difficile à maintenir où les Activités gèrent simultanément le réseau, les bases de données et l'UI. Le texte de l'UI est codé en dur, empêchant la traduction.

## 🛠 Cause Technique
`MainActivity.kt` contourne l'architecture ViewModel. Textes codés en dur `android:text="Orders (OF)"` dans `activity_main.xml`.

## 🚀 Correction Explicite (Étape par étape)
1. **Créer des ViewModels :** Déplacer `offlineManager.syncPendingScans()` dans une classe `MainViewModel.kt`.
2. **Extraire les Chaînes :** 
Dans `res/values/strings.xml` :
```xml
<string name="card_orders">Commandes (OF)</string>
```
Dans `activity_main.xml` :
```xml
android:text="@string/card_orders"
```

## ✅ Critères d'Acceptation
* `MainActivity.kt` ne fait qu'observer les LiveData/StateFlow et gérer les clics UI.
* Toutes les chaînes de texte codées en dur sont remplacées par des références `@string/`.
"""
}

out_dir = r"f:\OSM PROJECT\reviews\main-vs-pfe-analysis\jira-tickets"
os.makedirs(out_dir, exist_ok=True)

for ticket_id, content in tickets_fr.items():
    file_path = os.path.join(out_dir, f"{ticket_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully translated {len(tickets_fr)} markdown files to French in {out_dir}.")
