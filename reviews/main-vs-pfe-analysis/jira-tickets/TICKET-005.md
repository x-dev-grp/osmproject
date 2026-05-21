# TICKET-005 : Architecture - Duplication des DTOs (Split-Brain)

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
