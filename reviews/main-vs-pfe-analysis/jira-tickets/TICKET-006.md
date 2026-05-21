# TICKET-006 : Frontend - Correction du Port Backend (StatistiqueService)

**Priorité :** Haute  
**Composant :** `osm-ms-fe`

## 📝 Le Problème
Les pages de statistiques de Stock échouent à charger les données car les requêtes frontend sont envoyées au port `8080` au lieu du port de la Gateway `8084`.

## 🛠 Cause Technique
Dans `statistique.service.ts`, l'URL est codée en dur comme `http://localhost:8080/api/statistiques`.

## 🚀 Correction Explicite (Étape par étape)
1. Ceci sera corrigé en même temps que le TICKET-002, mais nécessite spécifiquement de s'assurer que la route correspond à la configuration de la Gateway.

**Exemple de Code (`statistique.service.ts`) :**
```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatistiqueService {
    // ✅ Changer le port et utiliser l'environnement
    private apiUrl = `${environment.apiUrl}/api/statistiques`;
}
```

## ✅ Critères d'Acceptation
* Les graphiques et données de statistiques se chargent correctement sans erreurs CORS ou de connexion réseau.
