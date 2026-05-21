# TICKET-003 : Mobile - Correction de l'IP de l'Émulateur

**Priorité :** Haute  
**Composant :** `osm-mobile` (Android)

## 📝 Le Problème
L'application Android utilise des adresses IP codées en dur (`http://10.0.2.2` ou `192.168.0.254`) pour la communication avec le backend. Cela empêche de générer un seul APK qui fonctionne en production ou sur des appareils physiques sans recompiler.

## 🛠 Cause Technique
Le fichier `Constants.kt` définit `BASE_URL` comme une constante statique de type String.

## 🚀 Correction Explicite (Étape par étape)
1. **Supprimer l'IP en dur :** Supprimer `BASE_URL` de `Constants.kt`.
2. **Utiliser BuildConfig :** Ajouter `buildConfigField` dans `build.gradle` (niveau app) pour différents flavors.

**Exemple de Code (`build.gradle`) :**
```groovy
android {
    buildTypes {
        debug {
            buildConfigField "String", "BASE_URL", "\"http://192.168.0.254:8084/\""
        }
        release {
            buildConfigField "String", "BASE_URL", "\"https://api.osm-production.com/\""
        }
    }
}
```

**Exemple de Code (`RetrofitClient.kt`) :**
```kotlin
Retrofit.Builder()
    // ✅ Utiliser BuildConfig au lieu de Constants
    .baseUrl(BuildConfig.BASE_URL)
    .client(client)
```

## ✅ Critères d'Acceptation
* Les appareils physiques peuvent contacter l'API simplement en changeant de build variant.
* `Constants.kt` ne contient plus d'adresses IP.
