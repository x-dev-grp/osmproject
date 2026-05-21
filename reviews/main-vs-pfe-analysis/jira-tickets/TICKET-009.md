# TICKET-009 : Frontend - Fuites de Mémoire Angular (Memory Leaks)

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
