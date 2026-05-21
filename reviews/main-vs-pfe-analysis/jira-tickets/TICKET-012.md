# TICKET-012 : Frontend - Standardisation UI/UX et Responsivité

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
