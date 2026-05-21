# TICKET-011 : Qualité - Standardisation de la Journalisation (Logging)

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
