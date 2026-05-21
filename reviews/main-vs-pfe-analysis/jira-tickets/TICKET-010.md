# TICKET-010 : Sécurité - Manque de Contrôle d'Accès (RBAC)

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
