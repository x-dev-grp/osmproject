# TICKET-001 : Backend - Atomicité de la Création d'Utilisateur et des Emails

**Priorité :** Haute / Critique  
**Composant :** `osm-sec` (`UserService.java`)

## 📝 Le Problème
Lors de la création d'un utilisateur ou de la réinitialisation d'un mot de passe, le système enregistre l'état de l'utilisateur en base de données puis envoie un e-mail. Si l'envoi de l'e-mail échoue (ex: serveur SMTP indisponible), la transaction n'est pas annulée (rollback). Cela laisse des utilisateurs "fantômes" en base qui ne peuvent pas se connecter et ne peuvent pas s'inscrire à nouveau.

## 🛠 Cause Technique
L'annotation `@Transactional` de Spring n'annule la transaction que sur les `RuntimeException` par défaut. La méthode `MailServiceImpl.sendEmail()` lève une `MessagingException` (qui est une exception contrôlée / checked). De ce fait, la transaction valide l'insertion en base avant que l'e-mail n'échoue. De plus, `resetPassword` manque totalement de l'annotation `@Transactional`.

## 🚀 Correction Explicite (Étape par étape)
1. **Mettre à jour les annotations :** Modifier `UserService.java` pour annuler explicitement sur toute Exception.
2. **Ajouter @Transactional à Reset Password :** Protéger le flux de réinitialisation.

**Exemple de Code (`UserService.java`) :**
```java
// Correctif 1 : Ajouter rollbackFor
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> addUser(@RequestBody SignupRequest signUpRequest) throws MessagingException {
    // ... logique existante ...
    mailService.sendEmail(user.getEmail(), "Activation", content);
}

// Correctif 2 : Protéger Reset Password
@Transactional(rollbackFor = Exception.class)
public ResponseEntity<?> resetPassword(@RequestBody ResetPasswordRequest request) throws MessagingException {
    // ... logique existante ...
}
```

## ✅ Critères d'Acceptation
* Lever une fausse `MessagingException` pendant la création d'un utilisateur annule correctement l'insertion en base.
* `resetPassword` est entièrement transactionnel.
