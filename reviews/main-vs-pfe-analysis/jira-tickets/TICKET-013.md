# TICKET-013 : Mobile - Vulnérabilités de Sécurité Critiques

**Priorité :** Critique  
**Composant :** `osm-mobile`

## 📝 Le Problème
L'application mobile stocke le `CLIENT_SECRET` OAuth et le `QR_SECRET` en texte clair. Les jetons JWT sont enregistrés sans chiffrement, et le trafic réseau imprime les mots de passe dans le logcat de l'appareil.

## 🛠 Cause Technique
`Constants.kt` contient les secrets. `SessionManager.kt` utilise les `SharedPreferences` classiques. `RetrofitClient.kt` utilise `HttpLoggingInterceptor.Level.BODY`.

## 🚀 Correction Explicite (Étape par étape)
1. **Supprimer le Log du Corps de Requête (`RetrofitClient.kt`) :**
```kotlin
private val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
}
```

2. **Chiffrer les SharedPreferences (`SessionManager.kt`) :**
```kotlin
// ✅ Utiliser EncryptedSharedPreferences
val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
val prefs = EncryptedSharedPreferences.create(
    Constants.PREF_NAME, masterKeyAlias, context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

## ✅ Critères d'Acceptation
* `CLIENT_SECRET` est totalement supprimé du contrôle de source (déplacé dans `local.properties`).
* Les jetons sont chiffrés de manière sécurisée sur le disque.
