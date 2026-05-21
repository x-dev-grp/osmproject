# Backlog Jira Détaillé - Stabilisation du Projet OSM

Ce document contient les tickets de bug prioritaires identifiés lors de la revue de code. Chaque ticket est expliqué en profondeur pour faciliter sa compréhension et sa résolution.

---

## [TICKET-001] Backend : Atomicité de la Création d'Utilisateur et des Emails
**Priorité :** Critique | **Composant :** `osm-sec` (`UserService`)

### 📝 Description Expliquée
**Le Problème :**
Actuellement, lorsqu'on crée un utilisateur ou qu'on réinitialise un mot de passe, le système fait deux choses : il écrit dans la base de données, puis il envoie un email. Si l'envoi de l'email échoue (serveur de mail en panne, mauvaise adresse), la base de données **ne revient pas en arrière**.

**Conséquences Fonctionnelles :**
1. **Comptes Fantômes** : Un utilisateur est créé en base de données mais ne reçoit jamais son mot de passe. Il ne peut pas se connecter, et il ne peut pas non plus se réinscrire car son email est déjà considéré comme "utilisé".
2. **Codes Inutilisables** : Lors d'un oubli de mot de passe, un code est généré et stocké, mais si le mail n'est pas reçu, l'utilisateur est bloqué car il ne peut pas demander un nouveau code immédiatement (le système considère qu'un code valide existe déjà).

**Cause Technique :**
*   Le mécanisme `@Transactional` de Spring ne surveille par défaut que les erreurs de type `RuntimeException`. L'envoi d'email génère souvent des exceptions vérifiées (*Checked Exceptions*) qui ne déclenchent pas l'annulation de la transaction.
*   Certaines méthodes, comme `resetPassword`, n'ont même pas l'annotation `@Transactional`.

**Solution Préconisée :**
*   Utiliser `@Transactional(rollbackFor = Exception.class)` pour forcer l'annulation de la sauvegarde en base si le mail échoue.
*   S'assurer que l'appel à `mailService.sendEmail()` est bien inclus dans le périmètre de la transaction.

> [!IMPORTANT]
> **Notes d'Audit (Senior Engineer) :** 
> *   *Vérification :* Confirmé dans `UserService.java`. 
> *   `MailServiceImpl.sendEmail` lève une `MessagingException` (Checked Exception). L'annotation `@Transactional` simple (présente sur `addUser` et `updateUser`) **ne fait pas de rollback** sur ce type d'exceptions.
> *   La méthode `resetPassword` ne possède *aucune* annotation `@Transactional`, ce qui sépare silencieusement la persistance en BDD de l'envoi d'email.
> *   *Action requise :* Ajouter `@Transactional(rollbackFor = Exception.class)` aux 3 méthodes et s'assurer que `updatePassword` l'inclut également.

---

## [TICKET-002] Frontend : Abstraction des URLs API (Environnement)
**Priorité :** Haute | **Composant :** `osm-ms-fe`

### 📝 Description Expliquée
**Le Problème :**
Le code source du frontend contient des adresses "en dur" comme `http://localhost:8084`. Cela signifie que l'application est soudée à votre machine locale.

**Conséquences Fonctionnelles :**
*   **Impossible de déployer** : Si vous mettez ce code sur un serveur de production, le navigateur de vos clients essaiera de contacter "localhost" (leur propre ordinateur) au lieu de votre serveur, et l'application ne fonctionnera pas.
*   **Maintenance lourde** : À chaque changement de serveur ou de port, vous devez modifier des dizaines de fichiers `.ts`.

**Cause Technique :**
Plusieurs services (`QualityService.ts`, `StatistiqueService.ts`, etc.) définissent une variable `private apiUrl` avec une chaîne de caractères fixe au lieu de lire la configuration globale d'Angular (`environment.ts`).

**Solution Préconisée :**
1. Centraliser toutes les URLs dans le fichier `src/environments/environment.ts`.
2. Injecter l'URL de base dans chaque service via `environment.apiUrl`.
3. Corriger le port de `StatistiqueService` qui pointe par erreur vers `8080` au lieu du port du Gateway (`8084`).

> [!WARNING]
> **Notes d'Audit (Senior Engineer) :** 
> *   *Vérification :* Confirmé via recherche globale. Le problème est présent dans : `stock.service.ts`, `statistique.service.ts`, `sku.service.ts`, `BomService.ts` et `QualityService.ts`.
> *   Dans `environment.prod.ts`, `apiUrl` est configuré à `''` (ce qui suggère que le proxy Caddy gère le trafic en production). Cependant, garder des URL en dur dans les services court-circuite cette configuration.
> *   *Action requise :* Nettoyer impérativement ces 5 services pour pointer vers `environment.apiUrl`.

---

## [TICKET-003] Mobile : Correction de l'IP de l'Émulateur
**Priorité :** Haute | **Composant :** `osm-mobile`

### 📝 Description Expliquée
**Le Problème :**
L'application mobile utilise l'IP `10.0.2.2`. C'est une IP "magique" qui ne fonctionne que dans l'émulateur Android fourni par Google.

**Conséquences Fonctionnelles :**
*   **Échec sur smartphone réel** : Si vous testez l'application sur un vrai téléphone Android connecté en Wi-Fi, elle ne pourra jamais contacter le serveur. Cela bloque les phases de test utilisateur finales (UAT).

**Cause Technique :**
Le fichier `Constants.kt` définit l'adresse de base du backend avec l'alias spécifique à l'émulateur Android.

**Solution Préconisée :**
1. Utiliser une configuration dynamique ou une IP de réseau local (ex: `192.168.1.50`) pour permettre les tests sur des appareils physiques.
2. Idéalement, passer par un fichier de configuration ou des "build flavors" pour différencier l'URL de test de l'URL de production.

> [!NOTE]
> **Notes d'Audit (Senior Engineer) :** 
> *   Vérification effectuée dans `Constants.kt`. Actuellement, la valeur est codée en dur à `const val BASE_URL = "http://192.168.0.254/"`.
> *   Bien que l'IP `10.0.2.2` ait été changée pour une IP de réseau local (`192.168.0.254`), le problème de fond persiste : **l'URL ne doit pas être codée en dur dans les constantes compilées**. Si le développeur change de réseau Wi-Fi ou déploie l'application, il doit recompiler le code source.
> *   *Action requise :* Mettre en place la configuration des *Build Variants* (ex: `debug`, `staging`, `release`) dans le fichier `build.gradle` d'Android pour gérer `BASE_URL` dynamiquement.

---

## [TICKET-004] Backend : Anti-pattern de Gestion des Exceptions
**Priorité :** Moyenne | **Composant :** `osm-prod` (FiltrationService), `osm-pack` (BomService)

### 📝 Description Expliquée
**Le Problème :**
Dans les nouveaux services ajoutés sur la branche `pfe`, les erreurs sont capturées puis relancées sous forme de `RuntimeException` génériques, effaçant ainsi la trace et le type d'erreur d'origine.

**Cause Technique :**
On retrouve ce modèle : `catch (Exception e) { throw new RuntimeException("...", e); }`. Les règles métier lèvent de simples `RuntimeException` au lieu d'exceptions personnalisées.

**Solution Préconisée :**
Remplacer les `RuntimeException` par des exceptions de domaine spécifiques et utiliser un `@ControllerAdvice`.

---

## [TICKET-005] Architecture : Duplication des DTOs (Split-Brain)
**Priorité :** Technique / Dette | **Composant :** Tout l'écosystème

### 📝 Description Expliquée
**Le Problème :**
Les DTOs sont copiés-collés dans les microservices (ex: `StorageUnitDto` existe dans `osm-prod` mais les clients Feign le redéfinissent) au lieu d'être partagés dans `osm-parent`.

**Solution Préconisée :**
Créer un module `osm-shared-dto` dans `osm-parent` et migrer toutes les classes DTO utilisées par les API REST publiques.

---

## [TICKET-008] Frontend : Restauration du Tableau de Bord (Dashboard)
**Priorité :** Haute | **Composant :** `osm-ms-fe`

### 📝 Description Expliquée
**Le Problème :**
Le composant `stock-dashboard.component.ts` a été entièrement mis en commentaire (*dead code*) sur la branche `pfe`. La page des statistiques est vide.

**Solution Préconisée :**
Retirer les commentaires du fichier et résoudre les erreurs de compilation bloquantes.

---

## [TICKET-009] Frontend : Fuites de Mémoire Angular (Memory Leaks)
**Priorité :** Moyenne | **Composant :** `osm-ms-fe`

### 📝 Description Expliquée
**Le Problème :**
De nombreux nouveaux composants s'abonnent aux données du backend (`.subscribe()`) mais n'implémentent jamais l'interface `OnDestroy` pour annuler ces abonnements.

**Solution Préconisée :**
Implémenter l'interface `OnDestroy` avec un `takeUntil(this.destroy$)` ou utiliser le `AsyncPipe`.

---

## [TICKET-010] Sécurité : Manque de Contrôle d'Accès (RBAC)
**Priorité :** Critique | **Composant :** Frontend (`osm-ms-fe`) & Backend (`osm-pack`, `osm-prod`)

### 📝 Description Expliquée
**Le Problème :**
Les nouvelles fonctionnalités de la branche `pfe` sont ouvertes à tous. N'importe quel utilisateur connecté peut appeler les API backend ou accéder aux écrans.

**Cause Technique :**
*   **Frontend** : Les nouveaux modules (`stock-routing.module.ts`) n'utilisent pas le `anyPermissionGuard` d'Angular.
*   **Backend** : Les nouveaux contrôleurs REST (`BomController.java`) n'ont pas les annotations `@PreAuthorize`.

**Solution Préconisée :**
1. Ajouter le garde `canActivate: [anyPermissionGuard([...])]` sur toutes les routes métier.
2. Ajouter l'annotation `@PreAuthorize` sur chaque méthode backend.

> [!CAUTION]
> **Notes d'Audit (Senior Engineer) :** 
> *   *Vérification :* C'est le problème le plus critique détecté à ce jour. La branche `pfe` a mis l'accent sur les fonctionnalités au détriment de la sécurité de base de l'architecture. À corriger impérativement avant toute mise en production.

---

## [TICKET-011] Qualité : Anti-patterns de Journalisation (Logging)
**Priorité :** Faible | **Composant :** Frontend (`osm-ms-fe`) & Backend (`osm-pack`, `osm-prod`)

### 📝 Description Expliquée
**Le Problème :**
La gestion des logs n'est pas standardisée. Les développeurs laissent des traces de débogage ("console.log", "System.out.println") directement dans le code de production.

**Conséquences Fonctionnelles :**
*   **Performance et Sécurité** : Côté Frontend, laisser des `console.log` en production peut ralentir le navigateur et exposer des données sensibles aux utilisateurs qui ouvrent la console. Côté Backend, `System.out.println` bloque les threads et ne permet pas d'exporter les logs vers des outils de surveillance (comme ELK ou Splunk).

**Cause Technique :**
*   **Backend** : Utilisation de `System.out.println` (ex: `SeuilAlerteService.java`) et `e.printStackTrace()` (ex: `StatistiqueService.java`) au lieu d'utiliser l'utilitaire d'entreprise existant `LoggingUtils` décrit dans le guide d'architecture.
*   **Frontend** : Des centaines d'occurrences de `console.log` ou `console.error` abandonnées dans les composants (ex: `stock-dashboard.component.ts`, `view-oil-transaction.component.ts`).

**Solution Préconisée :**
1. Backend : Remplacer systématiquement tous les `System.out.println` et `e.printStackTrace()` par des appels standardisés à la classe utilitaire `LoggingUtils` (par exemple : `LoggingUtils.logMethodEntry()`, `LoggingUtils.logError()`). Ne pas utiliser le logger `@Slf4j` par défaut pour conserver l'uniformité du projet.
2. Frontend : Retirer les `console.log` inutiles et configurer l'environnement de production d'Angular pour désactiver la console, ou utiliser un service de logging personnalisé.

> [!NOTE]
> **Notes d'Audit (Senior Engineer) :** 
> *   *Vérification :* Une recherche globale confirme que le standard du projet défini dans `apply-logging-patterns.md` utilise `LoggingUtils`. La branche `pfe` a complètement ignoré ce standard architectural, revenant à des impressions console basiques. L'utilisation obligatoire de `LoggingUtils` doit être rétablie. 

---

## [TICKET-012] Frontend : Standardisation UI/UX et Responsivité
**Priorité :** Moyenne | **Composant :** `osm-ms-fe` (Modules Stock, HR, Finance, etc.)

### 📝 Description Expliquée
**Le Problème :**
L'interface utilisateur des nouveaux modules développés dans la branche `pfe` souffre de graves lacunes en matière de standardisation, de performance d'affichage et de design responsif (mobile).

**Conséquences Fonctionnelles :**
*   **Performance** : Les tableaux de données s'affichent sans pagination. S'il y a des milliers de résultats, le navigateur plantera.
*   **Expérience Mobile** : L'application est inutilisable sur smartphone car les barres de recherche et filtres s'écrasent au lieu de s'empiler.
*   **Incohérence** : L'expérience utilisateur varie d'une page à l'autre (ex: menus déroulants vs boutons simples pour les mêmes actions).

**Cause Technique :**
*   **Duplication SCSS** : Plus de 250 lignes de CSS sont copiées-collées dans chaque composant (`article-list.component.scss`, `fournisseur-list.component.scss`) au lieu d'utiliser un composant global (ex: `<app-data-table>`).
*   **HTML Naïf** : Utilisation de `*ngFor` brut sans `<mat-paginator>` ou de pagination côté serveur. Grilles CSS (`grid-template-columns`) utilisées sans *Media Queries* au lieu des classes Bootstrap existantes (`col-md-6`).

**Solution Préconisée :**
1. Créer des composants partagés réutilisables (Header de page, Tableau de données) pour éliminer le code CSS dupliqué.
2. Implémenter une pagination sur tous les tableaux de liste.
3. Remplacer les grilles CSS rigides par le système de grille Bootstrap pour assurer la responsivité.
4. Harmoniser les menus d'actions (utiliser un standard Bootstrap ou Angular Material).

> [!WARNING]
> **Notes d'Audit (Senior Engineer) :** 
> *   *Vérification :* L'inspection du DOM confirme la violation du principe DRY (Don't Repeat Yourself) sur le SCSS. L'absence de pagination est une bombe à retardement pour la mise en production lorsque les vraies données clients seront injectées.

---

## [TICKET-013] Mobile : Vulnérabilités de Sécurité Critiques
**Priorité :** Critique | **Composant :** `osm-mobile`

### 📝 Description Expliquée
**Le Problème :**
L'application Android contient de multiples failles de sécurité béantes. Les secrets de l'entreprise sont écrits en dur dans le code, les jetons de connexion sont stockés en clair sur le téléphone, et le trafic réseau est entièrement logué en production.

**Conséquences Fonctionnelles :**
*   N'importe qui décompilant l'application (fichier `.apk`) peut extraire le `CLIENT_SECRET` et le `QR_SECRET` pour forger de faux QR codes ou pirater le système d'authentification. Sur un téléphone rooté, une application malveillante peut voler le `ACCESS_TOKEN` de l'utilisateur.

**Cause Technique :**
*   **Secrets en dur** : `Constants.kt` contient les clés privées au lieu du `BuildConfig` ou d'un appel API sécurisé.
*   **Stockage non sécurisé** : `SessionManager.kt` utilise le classique `SharedPreferences` (qui sauvegarde en clair au format XML) au lieu de `EncryptedSharedPreferences`.
*   **Fuite de Logs** : L'intercepteur Retrofit (`RetrofitClient.kt`) est configuré sur `HttpLoggingInterceptor.Level.BODY`, ce qui imprime tous les mots de passe et données personnelles dans le *Logcat* d'Android.

**Solution Préconisée :**
1. Migrer les secrets vers un fichier `local.properties` non suivi par Git et les injecter via `BuildConfig`.
2. Migrer `SessionManager` pour utiliser la bibliothèque AndroidX Security Crypto (`EncryptedSharedPreferences`).
3. Désactiver `HttpLoggingInterceptor` si `BuildConfig.DEBUG` est faux.

---

## [TICKET-014] Mobile : Dette Architecturale et Standards UI
**Priorité :** Moyenne | **Composant :** `osm-mobile`

### 📝 Description Expliquée
**Le Problème :**
Le code de l'application mobile ne respecte pas les standards modernes d'Android (Architecture MVVM) et l'interface utilisateur est construite avec des valeurs "codées en dur".

**Conséquences Fonctionnelles :**
*   L'application sera très difficile à maintenir, à tester unitairement, et il est actuellement impossible de la traduire facilement dans une autre langue (ex: Arabe, Anglais).

**Cause Technique :**
*   **Architecture Spaghettis** : `MainActivity.kt` instancie et appelle directement `OfflineManager` et la base de données locales. La gestion du réseau et des données hors-ligne devrait se faire dans des `ViewModel` séparés.
*   **Ressources UI en dur** : Les fichiers XML (ex: `activity_main.xml`) contiennent des textes en dur (`android:text="Orders (OF)"`) et le code Kotlin aussi (`"Bonjour, User!"`). Il n'y a pas d'utilisation des fichiers de ressources standard comme `strings.xml` ou `dimens.xml`.

**Solution Préconisée :**
1. Refactoriser les Activités pour utiliser l'architecture `ViewModel` et le pattern `Repository` pour la logique hors-ligne (`OfflineManager`).
2. Extraire toutes les chaînes de caractères vers `res/values/strings.xml` pour permettre l'internationalisation.