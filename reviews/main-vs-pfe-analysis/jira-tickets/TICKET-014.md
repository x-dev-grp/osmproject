# TICKET-014 : Mobile - Dette Architecturale (MVVM) et UI

**Priorité :** Moyenne  
**Composant :** `osm-mobile`

## 📝 Le Problème
Le code mobile est une structure "Spaghetti" difficile à maintenir où les Activités gèrent simultanément le réseau, les bases de données et l'UI. Le texte de l'UI est codé en dur, empêchant la traduction.

## 🛠 Cause Technique
`MainActivity.kt` contourne l'architecture ViewModel. Textes codés en dur `android:text="Orders (OF)"` dans `activity_main.xml`.

## 🚀 Correction Explicite (Étape par étape)
1. **Créer des ViewModels :** Déplacer `offlineManager.syncPendingScans()` dans une classe `MainViewModel.kt`.
2. **Extraire les Chaînes :** 
Dans `res/values/strings.xml` :
```xml
<string name="card_orders">Commandes (OF)</string>
```
Dans `activity_main.xml` :
```xml
android:text="@string/card_orders"
```

## ✅ Critères d'Acceptation
* `MainActivity.kt` ne fait qu'observer les LiveData/StateFlow et gérer les clics UI.
* Toutes les chaînes de texte codées en dur sont remplacées par des références `@string/`.
