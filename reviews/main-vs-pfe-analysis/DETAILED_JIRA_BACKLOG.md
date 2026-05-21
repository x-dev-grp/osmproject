# Detailed Jira Backlog - OSM Project Stabilization

This document provides a comprehensive breakdown of high-priority issues discovered during the code review. Each ticket includes a functional explanation, technical root cause, and a proposed fix.

---

## [TICKET-001] Backend: Fix Non-Atomic User Registration & Confirmation
**Priority:** High | **Component:** `osm-sec` (UserService)

### 🇬🇧 English Description
**Functional Impact:** 
When a new user is added or updated, the system sends an email with credentials. If the email service fails (e.g., SMTP timeout), the user remains saved in the database but has no way to access their account because they never received their temporary password. This leads to "Zombie Accounts" that must be manually deleted by a DBA.

**Technical Root Cause:**
The method `addUser` and `updateUser` are marked as `@Transactional`, but they perform the email sending *after* or *during* logic that doesn't account for checked exceptions. Furthermore, `resetPassword` lacks the `@Transactional` annotation entirely, meaning database commits and email sending are completely decoupled.

**Proposed Solution:**
1. Annotate all sensitive lifecycle methods with `@Transactional(rollbackFor = Exception.class)`.
2. Reorder logic to ensure that if `mailService.sendEmail()` throws an exception, the database transaction is rolled back.
3. **Location:** `UserService.java` (addUser, updateUser, resetPassword).

### 🇫🇷 Description en Français
**Impact Fonctionnel :**
Lorsqu'un utilisateur est ajouté, le système envoie ses identifiants par email. Si l'envoi échoue (ex: timeout SMTP), l'utilisateur est quand même créé en base mais ne peut pas se connecter car il n'a pas son mot de passe. Cela crée des "Comptes Fantômes" qui doivent être supprimés manuellement.

**Cause Technique :**
Les méthodes `addUser` et `updateUser` utilisent `@Transactional` mais ne gèrent pas correctement les exceptions liées au mail. La méthode `resetPassword` n'est même pas transactionnelle, ce qui sépare totalement la sauvegarde du code et son envoi.

**Solution Proposée :**
1. Ajouter `@Transactional(rollbackFor = Exception.class)` sur toutes les méthodes sensibles.
2. S'assurer que si l'envoi d'email échoue, la transaction en base de données est annulée.

---

## [TICKET-002] Frontend: Centralize API URLs in Environment Config
**Priority:** High | **Component:** `osm-ms-fe`

### 🇬🇧 English Description
**Functional Impact:**
The application is currently "hardcoded" to only work on a machine where the backend runs on `localhost`. It is impossible to deploy the application to a server (Cloud, VPS, etc.) without manually editing the source code of dozens of files.

**Technical Root Cause:**
Multiple services (`QualityService`, `StatistiqueService`, `BomService`, etc.) have private variables containing `http://localhost:8084`. This violates the Twelve-Factor App methodology for configuration.

**Proposed Solution:**
1. Refactor all Angular services to use `environment.apiUrl` from `src/environments/environment.ts`.
2. Fix the `StatistiqueService` which is currently targeting port `8080` (incorrect) instead of the Gateway port `8084`.

### 🇫🇷 Description en Français
**Impact Fonctionnel :**
L'application est configurée "en dur" pour ne fonctionner que sur une machine locale. Il est impossible de la déployer sur un serveur (Cloud, VPS) sans modifier manuellement des dizaines de fichiers source.

**Cause Technique :**
De nombreux services Angular utilisent des URLs codées en dur comme `http://localhost:8084`. Cela empêche toute flexibilité de déploiement.

**Solution Proposée :**
1. Refactoriser les services pour utiliser `environment.apiUrl` défini dans `environment.ts`.
2. Corriger le port `8080` dans `StatistiqueService` qui devrait pointer vers le Gateway (`8084`).

---

## [TICKET-003] Mobile: Fix Hardcoded Emulator IP
**Priority:** High | **Component:** `osm-mobile`

### 🇬🇧 English Description
**Functional Impact:**
The mobile application only works on Android Emulators. If installed on a real smartphone, the app fails to connect to the backend because it tries to reach the local loopback address of the emulator.

**Technical Root Cause:**
The `Constants.kt` file uses `10.0.2.2`, which is a special alias for the host machine's localhost only available inside the Android emulator environment.

**Proposed Solution:**
1. Replace `10.0.2.2` with an environment-based constant or use a LAN IP (e.g., `192.168.x.x`) for development testing on physical devices.

### 🇫🇷 Description en Français
**Impact Fonctionnel :**
L'application mobile ne fonctionne que sur émulateur. Sur un vrai téléphone, elle ne peut pas se connecter au backend car elle tente d'utiliser une IP virtuelle propre à l'émulateur.

**Cause Technique :**
Le fichier `Constants.kt` utilise l'IP `10.0.2.2`, qui est un alias réservé uniquement aux émulateurs Android pour contacter la machine hôte.

**Solution Proposée :**
1. Remplacer `10.0.2.2` par une constante configurable ou utiliser une IP réseau locale (ex: `192.168.x.x`) pour les tests sur appareils physiques.
