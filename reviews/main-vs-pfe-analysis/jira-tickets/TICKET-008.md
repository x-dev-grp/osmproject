# TICKET-008 : Frontend - Restauration du Tableau de Bord (Dashboard)

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
