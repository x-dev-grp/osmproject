# TICKET-007 : Architecture - Standardisation des Entités et Validations

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
