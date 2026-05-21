# TICKET-002 : Frontend - Abstraction des URLs API (Environnement)

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
