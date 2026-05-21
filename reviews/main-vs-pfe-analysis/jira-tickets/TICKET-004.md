# TICKET-004 : Backend - Anti-pattern de Gestion des Exceptions (RuntimeException)

**Priorité :** Moyenne  
**Composant :** `osm-prod`, `osm-pack`

## 📝 Le Problème
Les exceptions du domaine sont interceptées et encapsulées dans des `RuntimeException` génériques. Cela force le frontend à gérer des erreurs 500 Internal Server Error génériques au lieu de réponses 400 ou 404 propres.

## 🛠 Cause Technique
Les contrôleurs (comme `BomController.java`) utilisent des blocs `try/catch` manuels retournant `ResponseEntity.status(HttpStatus.BAD_REQUEST)`. Les services (comme `FiltrationService.java`) interceptent toutes les exceptions et font `throw new RuntimeException("...", e)`.

## 🚀 Correction Explicite (Étape par étape)
1. **Créer des Exceptions Personnalisées :** Ex: `ResourceNotFoundException`.
2. **Implémenter @ControllerAdvice :** Les gérer globalement.

**Exemple de Code (`GlobalExceptionHandler.java` dans `osm-pack`) :**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<?> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", ex.getMessage()));
    }
}
```

**Exemple de Code (`BomController.java`) :**
```java
// ❌ SUPPRIMER le try/catch manuel :
@GetMapping("/{id}")
public ResponseEntity<?> getBomById(@PathVariable UUID id) {
    // ✅ RETOURNER DIRECTEMENT LE DTO. Laisser le ControllerAdvice gérer les erreurs.
    return ResponseEntity.ok(bomService.getBomById(id));
}
```

## ✅ Critères d'Acceptation
* Les contrôleurs n'ont plus de `try/catch` manuel pour la logique métier.
* HTTP 404 est correctement retourné quand une ressource est manquante.
