# Explication complète de la traçabilité

## 1. Objet

Dans ce projet, la traçabilité ne désigne pas le tracing technique des requêtes HTTP.  
Elle désigne la **généalogie métier de l'huile** depuis la réception jusqu'à l'expédition.

Chaîne cible :

```text
Réception -> Contrôle qualité -> Lot de traçabilité racine -> Filtration -> Lot de traçabilité filtré -> OF -> Étiquette -> Expédition
```

Le point central du refactoring est la séparation entre :

- `lotVracId` : identifiant opérationnel de cuve / stockage
- `traceabilityLotId` : identifiant métier immuable utilisé comme ancre de généalogie

---

## 2. Répartition par module

- `osm-prod` : vérité métier de la généalogie huile
- `osm-cond` : propagation de cette généalogie dans les OF, étiquettes et expéditions
- `osm-ms-fe` : affichage et reconstitution visuelle de la chaîne
- `osm-parent/comunicator` : DTOs partagés entre services

---

## 3. Le concept clé : `TraceabilityLot`

Le coeur du système est l'entité `TraceabilityLot` dans `osm-prod`.

### Rôle

Un `TraceabilityLot` représente un **lot métier immuable**.  
Il capture un état de généalogie à un instant donné, au lieu de dépendre uniquement de l'état mutable d'une cuve.

### Extrait de code

```java
@Entity
@Table(name = "traceability_lot")
@Getter
@Setter
@Audited
public class TraceabilityLot extends BaseEntity {

    @Column(name = "lot_number", nullable = false, length = 120)
    private String lotNumber;

    @Enumerated(EnumType.STRING)
    @Column(name = "source_type", nullable = false, length = 40)
    private TraceabilitySourceType sourceType;

    @Column(name = "root_reception_id")
    private UUID rootReceptionId;

    @Column(name = "parent_lot_id")
    private UUID parentLotId;

    @Column(name = "storage_unit_id")
    private UUID storageUnitId;

    @Column(name = "filtration_operation_id")
    private UUID filtrationOperationId;

    @Column(name = "captured_at", nullable = false)
    private LocalDateTime capturedAt;

    @Column(name = "active", nullable = false)
    private Boolean active = true;

    @Lob
    @Column(name = "source_snapshot_json", columnDefinition = "TEXT")
    private String sourceSnapshotJson;
}
```

### Signification des champs

- `lotNumber` : numéro métier du lot
- `sourceType` : origine du lot (`RECEPTION`, `TRITURATION`, `FILTRATION`)
- `rootReceptionId` : racine métier de toute la branche
- `parentLotId` : lien vers le lot immuable précédent
- `storageUnitId` : cuve actuellement associée
- `filtrationOperationId` : opération de filtration qui a produit ce lot
- `capturedAt` : date de capture de l'état
- `active` : lot actif pour une cuve donnée
- `sourceSnapshotJson` : snapshot JSON de contexte

### Enum source

```java
public enum TraceabilitySourceType {
    RECEPTION,
    TRITURATION,
    FILTRATION
}
```

---

## 4. Structure SQL

Le support base de données est posé dans `osm-prod`.

### Extrait SQL

```sql
CREATE TABLE IF NOT EXISTS traceability_lot (
    id uuid PRIMARY KEY,
    tenant_id uuid,
    is_deleted boolean NOT NULL DEFAULT false,
    created_by varchar(255),
    created_date timestamp,
    last_modified_by varchar(255),
    last_modified_date timestamp,
    external_id uuid,
    qr_hex varchar(6),
    qr_image_base64 text,

    lot_number varchar(120) NOT NULL,
    source_type varchar(40) NOT NULL,
    source_entity_id uuid,
    root_reception_id uuid,
    parent_lot_id uuid,
    storage_unit_id uuid,
    filtration_operation_id uuid,
    quality_grade varchar(255),
    oil_variety varchar(255),
    quantity double precision,
    captured_at timestamp NOT NULL,
    active boolean NOT NULL DEFAULT true,
    source_snapshot_json text
);
```

### Ce que cela implique

- la traçabilité est stockée explicitement
- la relation parent/enfant est persistée
- la réception racine est persistée
- l'état de contexte est historisé dans un snapshot JSON

Important : les scripts SQL existent, mais le dépôt ne semble pas exécuter automatiquement Flyway/Liquibase à ce stade. Le rollout reste manuel.

---

## 5. Création du lot racine

Le lot racine n'est pas créé au moment exact de la réception.  
Il est créé **à la demande** quand le système en a besoin.

### Méthode clé

```java
@Transactional
public TraceabilityLot ensureRootLotForStorageUnit(StorageUnit storageUnit) {
    return traceabilityLotRepository
            .findFirstByStorageUnitIdAndActiveTrueAndIsDeletedFalseOrderByCapturedAtDesc(storageUnit.getId())
            .orElseGet(() -> createRootLot(storageUnit));
}
```

### Création effective

```java
private TraceabilityLot createRootLot(StorageUnit storageUnit) {
    UnifiedDelivery reception = oilTransactionService.findByStorageUnitId(storageUnit.getId()).stream()
            .filter(tx -> tx.getTransactionType() == TransactionType.RECEPTION_IN)
            .map(OilTransaction::getReception)
            .filter(java.util.Objects::nonNull)
            .findFirst()
            .orElse(null);

    TraceabilityLot rootLot = new TraceabilityLot();
    rootLot.setLotNumber(resolveLotNumber(storageUnit));
    rootLot.setSourceType(resolveRootSourceType(reception));
    rootLot.setSourceEntityId(reception != null ? reception.getId() : storageUnit.getId());
    rootLot.setRootReceptionId(reception != null ? reception.getId() : null);
    rootLot.setParentLotId(null);
    rootLot.setStorageUnitId(storageUnit.getId());
    rootLot.setCapturedAt(LocalDateTime.now());
    rootLot.setActive(true);
    rootLot.setSourceSnapshotJson(buildRootSnapshot(storageUnit, reception));

    deactivateActiveLotsForStorage(storageUnit.getId());
    return traceabilityLotRepository.save(rootLot);
}
```

### Lecture métier

- le système cherche la réception d'origine via l'historique des transactions
- il crée un lot immuable racine
- ce lot devient le lot actif de la cuve
- la racine de généalogie est `rootReceptionId`

---

## 6. Création du lot filtré

La création d'un lot de traçabilité filtré se produit à la fin d'une filtration.

### Point d'entrée

```java
traceabilityLotService.ensureRootLotForStorageUnit(sourceUnit);
...
traceabilityLotService.createFilteredLot(sourceUnit, targetUnit, operation, volumeAfter);
```

### Création du lot enfant

```java
@Transactional
public TraceabilityLot createFilteredLot(StorageUnit sourceUnit, StorageUnit targetUnit, FiltrationOperation operation,
        Double quantity) {
    TraceabilityLot parentLot = ensureRootLotForStorageUnit(sourceUnit);

    TraceabilityLot filteredLot = new TraceabilityLot();
    filteredLot.setLotNumber(operation.getTargetLotNumber());
    filteredLot.setSourceType(TraceabilitySourceType.FILTRATION);
    filteredLot.setSourceEntityId(operation.getId());
    filteredLot.setRootReceptionId(parentLot.getRootReceptionId());
    filteredLot.setParentLotId(parentLot.getId());
    filteredLot.setStorageUnitId(targetUnit.getId());
    filteredLot.setFiltrationOperationId(operation.getId());
    filteredLot.setQuantity(quantity);
    filteredLot.setCapturedAt(LocalDateTime.now());
    filteredLot.setActive(true);

    deactivateActiveLotsForStorage(targetUnit.getId());
    return traceabilityLotRepository.save(filteredLot);
}
```

### Logique métier

Le lot filtré :

- hérite de la racine via `rootReceptionId`
- pointe vers son parent via `parentLotId`
- devient l'ancre immuable du produit filtré
- est associé à la cuve cible

Autrement dit, la filtration crée un **nouveau maillon de généalogie**, pas juste une mutation de cuve.

---

## 7. Résolution de l'ancre de traçabilité

Le backend production accepte deux types d'identifiants :

- un vrai `traceabilityLotId`
- un ancien identifiant de cuve `storageUnitId`

### Extrait

```java
@Transactional(readOnly = true)
public Optional<TraceabilityLot> resolveByLotOrStorage(UUID lotOrStorageId) {
    Optional<TraceabilityLot> directLot = traceabilityLotRepository.findByIdAndIsDeletedFalse(lotOrStorageId);
    if (directLot.isPresent()) {
        return directLot;
    }

    return traceabilityLotRepository.findFirstByStorageUnitIdAndActiveTrueAndIsDeletedFalseOrderByCapturedAtDesc(lotOrStorageId);
}
```

### Conséquence

La transition ancien modèle -> nouveau modèle reste compatible.  
Les anciennes références basées sur la cuve continuent de fonctionner.

---

## 8. Construction de la généalogie

La généalogie complète est exposée par :

```java
@RestController
@RequestMapping("/api/production/traceability")
public class GenealogyController {

    @GetMapping("/genealogy/{storageUnitId}")
    public ResponseEntity<ApiResponse<GenealogyDto>> getGenealogy(@PathVariable UUID storageUnitId) {
        GenealogyDto data = genealogyService.getFullGenealogy(storageUnitId);
        return ResponseEntity.ok(new ApiResponse<>(true, "Genealogy fetched successfully", data));
    }
}
```

### DTO retourné

```java
@Data
public class GenealogyDto {
    private UUID traceabilityLotId;
    private String traceabilitySourceType;
    private UUID rootReceptionId;
    private UUID storageUnitId;
    private String lotNumber;
    private String storageUnitName;
    private Map<String, String> filteredQualityControls;
    private List<FiltrationStepDto> filtrations = new ArrayList<>();
    private List<RootSourceDto> rootSources = new ArrayList<>();
    private List<IntakeStepDto> intakeChain = new ArrayList<>();
}
```

### Choix principal

```java
@Transactional(readOnly = true)
public GenealogyDto getFullGenealogy(UUID lotOrStorageId) {
    Optional<TraceabilityLot> traceabilityLotOpt = traceabilityLotService.resolveByLotOrStorage(lotOrStorageId);
    if (traceabilityLotOpt.isPresent()) {
        return buildFromTraceabilityLot(traceabilityLotOpt.get());
    }

    StorageUnit unit = storageUnitRepo.findById(lotOrStorageId)
            .orElseThrow(() -> new RuntimeException("Storage unit or traceability lot not found"));

    GenealogyDto dto = new GenealogyDto();
    dto.setStorageUnitId(unit.getId());
    dto.setLotNumber(unit.getLotNumber());
    dto.setStorageUnitName(unit.getName());

    buildLegacyFiltrationChain(unit.getLotNumber(), unit.getId(), dto);
    dto.setIntakeChain(buildIntakeChainForStorageUnit(unit.getId()));
    supplementRootSourcesFromIntake(dto);
    return dto;
}
```

### Deux modes

#### Mode moderne

Si un `TraceabilityLot` existe :

- on reconstruit la chaîne via les parents
- on ajoute les filtrations
- on ajoute les contrôles qualité
- on ajoute les sources racines
- on ajoute la chaîne d'entrée en cuve

#### Mode legacy

Si aucun `TraceabilityLot` n'existe :

- on retombe sur les numéros de lot et la cuve
- on reconstruit la chaîne à partir de l'état opérationnel

---

## 9. Reconstruction de la chaîne parent/enfant

### Extrait

```java
private void buildTraceabilityChain(TraceabilityLot traceabilityLot, GenealogyDto dto) {
    TraceabilityLot current = traceabilityLot;
    while (current != null) {
        if (current.getSourceType() == TraceabilitySourceType.FILTRATION && current.getFiltrationOperationId() != null) {
            TraceabilityLot finalCurrent = current;
            filtrationRepo.findByIdAndIsDeletedFalse(current.getFiltrationOperationId())
                    .ifPresent(operation -> dto.getFiltrations().add(toFiltrationStep(operation, finalCurrent.getId())));
        }

        if (current.getParentLotId() == null) {
            break;
        }

        current = traceabilityLotService.findById(current.getParentLotId()).orElse(null);
    }
}
```

### Lecture

Le service part du lot courant puis remonte vers le parent, puis le parent du parent, jusqu'à la racine.  
Chaque étape de filtration est convertie en `FiltrationStepDto`.

---

## 10. Contrôle qualité dans la chaîne

Les résultats QC peuvent être liés :

- directement à une réception
- à une opération de filtration
- à un `traceabilityLotId`

### Modèle QC

```java
@Column(name = "filtration_operation_id")
private UUID filtrationOperationId;

@Column(name = "traceability_lot_id")
private UUID traceabilityLotId;
```

### Sauvegarde QC filtration

```java
UUID traceabilityLotId = traceabilityLotRepository
        .findFirstByFiltrationOperationIdAndIsDeletedFalseOrderByCapturedAtDesc(filtrationOperationId)
        .map(com.osm.oilproductionservice.model.TraceabilityLot::getId)
        .orElse(null);

entity.setFiltrationOperationId(filtrationOperationId);
entity.setTraceabilityLotId(dto.getTraceabilityLotId() != null ? dto.getTraceabilityLotId() : traceabilityLotId);
```

### Résolution QC dans la généalogie

```java
private Map<String, String> resolveQualityControls(UUID traceabilityLotId, UUID filtrationOperationId) {
    List<QualityControlResult> results = traceabilityLotId != null
            ? qualityControlResultRepository.findByTraceabilityLotIdAndIsDeletedFalse(traceabilityLotId)
            : List.of();

    if (results.isEmpty() && filtrationOperationId != null) {
        results = qualityControlResultRepository.findByFiltrationOperationIdAndIsDeletedFalse(filtrationOperationId);
    }
    ...
}
```

### Conséquence

Le système privilégie le lien métier immuable `traceabilityLotId`, puis retombe sur le lien opérationnel `filtrationOperationId`.

---

## 11. Chaîne d'entrée en cuve

Une partie importante de la traçabilité est la reconstruction de la chaîne :

- réception olive
- réception huile
- entrée en cuve

### Extrait

```java
private List<IntakeStepDto> buildIntakeChainForStorageUnit(UUID storageUnitId) {
    List<OilTransaction> receptionTxs = oilTransactionRepository
            .findAllByStorageUnitDestinationIdAndTransactionTypeAndIsDeletedFalseOrderByCreatedDateAsc(
                    storageUnitId, TransactionType.RECEPTION_IN);
    ...
    for (OilTransaction receptionTx : receptionTxs) {
        UnifiedDelivery oilDelivery = resolveOilDelivery(receptionTx);
        ...
        chain.add(toIntakeStepFromDelivery(oilDelivery, "OIL_RECEPTION"));
        chain.add(toIntakeStepFromTransaction(receptionTx, storageUnit, oilDelivery));
    }
    return chain;
}
```

### Pourquoi c'est important

La traçabilité ne s'arrête pas à la filtration.  
Elle remonte jusqu'aux entrées physiques de matière.

---

## 12. Propagation vers les OF dans `osm-cond`

L'ordre de fabrication porte désormais les deux identifiants :

```java
@Column(name = "lot_vrac_id")
private UUID lotVracId;

@Column(name = "traceability_lot_id")
private UUID traceabilityLotId;
```

### Résolution à la création / mise à jour

```java
if (dto.getLotVracId() != null) {
    dto.setTraceabilityLotId(resolveTraceabilityLotId(dto.getLotVracId()));
}
```

### Logique de résolution

```java
private UUID resolveTraceabilityLotId(UUID lotVracId) {
    try {
        ApiResponse<StorageUnitDto> storageResponse = productionStorageClient.getStorageUnit(lotVracId);
        if (storageResponse == null || !storageResponse.isSuccess() || storageResponse.getData() == null) {
            throw new RuntimeException("Cuve d'huile introuvable (ID: " + lotVracId + ")");
        }

        ApiResponse<com.osm.conditioning.expedition.dto.GenealogyDto> genealogyResponse =
                productionStorageClient.getGenealogy(lotVracId);
        if (genealogyResponse != null && genealogyResponse.isSuccess() && genealogyResponse.getData() != null
                && genealogyResponse.getData().getTraceabilityLotId() != null) {
            return genealogyResponse.getData().getTraceabilityLotId();
        }

        return lotVracId;
    } catch (RuntimeException e) {
        throw e;
    } catch (Exception e) {
        log.warn("Erreur validation lot vrac {}: {}", lotVracId, e.getMessage());
        throw new RuntimeException("Impossible de valider le lot vrac selectionne", e);
    }
}
```

### Point critique

Le fallback `return lotVracId` signifie que `traceabilityLotId` peut encore contenir une ancienne référence de cuve si la migration métier n'est pas complète.  
Le champ est donc conceptuellement une ancre immuable, mais pratiquement encore hybride.

### Backfill paresseux

```java
private void ensureTraceabilityLotId(OrdreFabrication of) {
    if (of == null || of.getTraceabilityLotId() != null || of.getLotVracId() == null) {
        return;
    }

    UUID resolved = resolveTraceabilityLotId(of.getLotVracId());
    if (resolved != null && !resolved.equals(of.getTraceabilityLotId())) {
        of.setTraceabilityLotId(resolved);
        ofRepository.save(of);
    }
}
```

---

## 13. Propagation vers les étiquettes

Les étiquettes stockent aussi :

- `lotId`
- `traceabilityLotId`

### Modèle

```java
@Column(name = "lot_id", nullable = false)
private UUID lotId;

@Column(name = "traceability_lot_id")
private UUID traceabilityLotId;
```

### Génération d'étiquette

```java
StorageUnitDto storageUnit = response.getData();
GenealogyDto genealogy = fetchGenealogy(request.getLotId());

LabelContent labelContent = new LabelContent();
labelContent.setLotId(request.getLotId());
labelContent.setTraceabilityLotId(resolveTraceabilityLotId(request.getLotId(), request.getTraceabilityLotId(), genealogy));
```

### Résolution

```java
private UUID resolveTraceabilityLotId(UUID lotId, UUID requestedTraceabilityLotId, GenealogyDto genealogy) {
    if (requestedTraceabilityLotId != null) {
        return requestedTraceabilityLotId;
    }
    if (genealogy != null && genealogy.getTraceabilityLotId() != null) {
        return genealogy.getTraceabilityLotId();
    }
    return lotId;
}
```

### Même point critique

Le fallback final est encore `lotId`.  
Là aussi, la migration reste backward-compatible.

---

## 14. Snapshots de preuve sur les étiquettes

L'étiquette ne stocke pas seulement un identifiant.  
Elle stocke des **preuves de contexte** sérialisées.

### Snapshots enregistrés

```java
addSnapshot(
        labelContent,
        LabelSourceType.FILTERED_LOT,
        labelContent.getTraceabilityLotId() != null ? labelContent.getTraceabilityLotId() : storageUnit.getId(),
        storageUnit.getLotNumber(),
        buildFilteredLotSnapshot(storageUnit, genealogy, labelContent)
);
addSnapshot(labelContent, LabelSourceType.PACKAGING, packaging.getId(), packaging.getCode(), packaging);
addSnapshot(labelContent, LabelSourceType.OPERATOR, currentUser.id(), currentUser.displayName(), currentUser.snapshot());
addSnapshot(labelContent, LabelSourceType.COMPANY_PROFILE, companyProfile.getId(), companyProfile.getLegalName(), companyProfile);
```

### Snapshot principal

```java
private Map<String, Object> buildFilteredLotSnapshot(
        StorageUnitDto storageUnit,
        GenealogyDto genealogy,
        LabelContent labelContent
) {
    Map<String, Object> snapshot = new LinkedHashMap<>();
    snapshot.put("storageUnitId", storageUnit.getId());
    snapshot.put("storageUnitName", storageUnit.getName());
    snapshot.put("traceabilityLotId", labelContent.getTraceabilityLotId());
    snapshot.put("rootReceptionId", genealogy != null ? genealogy.getRootReceptionId() : null);
    snapshot.put("traceabilitySourceType", genealogy != null ? genealogy.getTraceabilitySourceType() : null);
    snapshot.put("lotNumber", storageUnit.getLotNumber());
    snapshot.put("qualityGrade", storageUnit.getQualityGrade());
    snapshot.put("oilVariety", storageUnit.getOilType());
    snapshot.put("genealogy", genealogy);
    return snapshot;
}
```

### Intérêt

L'étiquette conserve une preuve autonome :

- cuve filtrée
- lot métier
- origine racine
- type de source
- généalogie complète

Cela la rend utile même si certaines données amont changent ensuite.

---

## 15. Validation de la complétude des étiquettes

Le service refuse de considérer une étiquette comme saine si certaines données critiques sont absentes.

### Extrait

```java
validateNotNull(issues, labelContent.getLotId(), "lotId", "Lot filtre absent");
validateNotNull(issues, labelContent.getTraceabilityLotId(), "traceabilityLotId", "Traceabilite lot absente");
validateNotNull(issues, labelContent.getPackagingId(), "packagingId", "Packaging absent");
validateNotBlank(issues, labelContent.getLotNumber(), "lotNumber", "Numero de lot indisponible");
```

### Lecture

L'ancre de traçabilité est devenue une condition métier explicite.

---

## 16. Traçabilité projet et expédition

Le service d'expédition reconstruit une vue globale à partir des OF.

### API

```java
@GetMapping("/project/{projectId}/traceability")
public ResponseEntity<Map<String, Object>> getProjectTraceability(@PathVariable UUID projectId) {
    return ResponseEntity.ok(expeditionService.getProjectTraceability(projectId));
}

@GetMapping("/{id}/traceability")
public ResponseEntity<Map<String, Object>> getExpeditionTraceability(@PathVariable UUID id) {
    return ResponseEntity.ok(expeditionService.getExpeditionTraceability(id));
}
```

### Construction principale

```java
private Map<String, Object> buildTraceabilityMap(UUID projectId, List<OrdreFabrication> ofs, Expedition expedition) {
    Map<String, Object> snapshot = new LinkedHashMap<>();
    Map<String, GenealogyDto> oilGenealogy = new LinkedHashMap<>();
    Map<String, Object> ofDetails = new LinkedHashMap<>();
    Map<String, List<Map<String, Object>>> packagedLabelsByLot = new LinkedHashMap<>();

    for (OrdreFabrication of : ofs) {
        ensureTraceabilityLotId(of);
        ...
        UUID genealogyAnchor = of.getTraceabilityLotId() != null ? of.getTraceabilityLotId() : of.getLotVracId();
        if (genealogyAnchor == null) {
            continue;
        }

        String anchorKey = genealogyAnchor.toString();
        ApiResponse<GenealogyDto> response = productionStorageClient.getGenealogy(genealogyAnchor);
        if (response != null && response.isSuccess() && response.getData() != null) {
            oilGenealogy.put(anchorKey, response.getData());
            packagedLabelsByLot.put(anchorKey, labelSnapshotsForLot(of));
        }
    }

    snapshot.put("ofDetails", ofDetails);
    snapshot.put("oilGenealogy", oilGenealogy);
    snapshot.put("packagedLabelsByLot", packagedLabelsByLot);
    snapshot.put("eventChains", TraceabilityEventTreeBuilder.buildChains(
            projectId, ofs, oilGenealogy, packagedLabelsByLot, projectExpeditions));
    snapshot.put("capturedAt", java.time.LocalDateTime.now().toString());
    snapshot.put("live", expedition == null || expedition.getTraceabilitySnapshotJson() == null);

    return snapshot;
}
```

### Ce que contient la vue

- `ofDetails` : détails OF
- `oilGenealogy` : généalogie par ancre
- `packagedLabelsByLot` : étiquettes groupées par lot
- `eventChains` : timeline événementielle
- `capturedAt` : timestamp de génération
- `live` : vue live ou snapshot

---

## 17. Snapshot figé à la validation d'expédition

La capture n'a pas lieu à l'expédition finale.  
Elle a lieu au moment de la **validation**.

### Extrait

```java
public ExpeditionDto validate(UUID expeditionId, ExpeditionActionRequest request) {
    Expedition expedition = findExpedition(expeditionId);
    if (expedition.getStatus() != ExpeditionStatus.READY) {
        throw new IllegalStateException("La validation exige une expedition READY");
    }

    traceabilityService.assertTraceabilityComplete(expedition);

    expedition.setStatus(ExpeditionStatus.VALIDATED);
    expedition.setValidatedAt(LocalDateTime.now());

    traceabilityService.captureTraceabilitySnapshot(expedition);

    Expedition saved = expeditionRepository.save(expedition);
    return toDto(saved);
}
```

### Capture

```java
@Transactional
public String captureTraceabilitySnapshot(Expedition expedition) {
    List<OrdreFabrication> ofs = resolveExpeditionOfs(expedition);
    UUID projectId = expedition.getProjet() != null ? expedition.getProjet().getId() : null;
    Map<String, Object> snapshot = buildTraceabilityMap(projectId, ofs, expedition);

    String json = objectMapper.writeValueAsString(snapshot);
    expedition.setTraceabilitySnapshotJson(json);
    return json;
}
```

### Sens métier

À partir de ce moment, l'expédition porte sa propre trace figée de justification.

---

## 18. Contrôle de complétude avant validation

Avant de figer le snapshot, le système vérifie qu'il y a une origine documentée.

### Extrait

```java
for (OrdreFabrication of : ofs) {
    ensureTraceabilityLotId(of);
    UUID anchor = of.getTraceabilityLotId() != null ? of.getTraceabilityLotId() : of.getLotVracId();
    if (anchor == null) {
        issues.add("OF " + valueOrEmpty(of.getCode()) + " : aucun lot vrac ou lot de tracabilite");
        continue;
    }

    ApiResponse<GenealogyDto> response = productionStorageClient.getGenealogy(anchor);
    if (response == null || !response.isSuccess() || response.getData() == null) {
        issues.add("OF " + valueOrEmpty(of.getCode()) + " : genealogie huile introuvable");
        continue;
    }
    GenealogyDto genealogy = response.getData();
    if (!TraceabilityEventTreeBuilder.hasDocumentedOilOrigin(genealogy)) {
        issues.add("OF " + valueOrEmpty(of.getCode()) + " : origine reception ou trituration manquante");
    }
}
```

### Règle métier

Une expédition ne doit pas être validée si l'origine matière n'est pas démontrable.

---

## 19. Construction de la timeline événementielle

La vue projet / expédition ne montre pas seulement des objets.  
Elle reconstruit une chronologie métier.

### Construction d'une chaîne

```java
chain.put("ofId", of.getId() != null ? of.getId().toString() : "");
chain.put("ofCode", of.getCode());
chain.put("traceabilityLotId", of.getTraceabilityLotId() != null ? of.getTraceabilityLotId().toString() : "");
chain.put("lotVracId", of.getLotVracId() != null ? of.getLotVracId().toString() : "");
chain.put("genealogyAnchor", anchorKey != null ? anchorKey : "");
chain.put("events", buildEventsForOf(of, genealogy, labels, expeditionsByOfId.get(of.getId())));
```

### Exemples d'événements injectés

```java
events.add(event(
        filtId,
        lastParentId,
        "FILTRATION",
        phaseLabel("PRODUCTION"),
        "Filtration -> lot " + nullToEmpty(step.getTargetLotNumber()),
        parseTimestamp(step.getTimestamp()),
        filtrationDetails(step)));
```

```java
events.add(event(
        ofId,
        ofParent,
        "OF",
        phaseLabel("CONDITIONING"),
        "Ordre de fabrication " + nullToEmpty(of.getCode()),
        of.getCreatedDate(),
        ofEventDetails(of)));
```

```java
events.add(event(
        eventId("EXPEDITION", expedition.getId()),
        ofId,
        "EXPEDITION",
        phaseLabel("EXPEDITION"),
        "Expedition " + nullToEmpty(expedition.getExpeditionNumber()),
        expeditionEventTimestamp(expedition),
        expeditionEventDetails(expedition)));
```

### Lecture

La chaîne peut contenir :

- réception olive
- réception huile
- entrée en cuve
- filtration
- QC filtration
- stockage final
- OF
- démarrage OF
- fin OF
- étiquetage
- expédition

---

## 20. Partie frontend

Le frontend consomme la généalogie via un service Angular simple.

### Service Angular

```ts
@Injectable({ providedIn: 'root' })
export class ProductionTraceabilityService {
  private readonly baseUrl = `${environment.apiUrl}/api/production/traceability`;

  constructor(private readonly http: HttpClient) {}

  getGenealogy(anchorId: string): Observable<ProductionGenealogy> {
    return this.http
      .get<ApiResponse<ProductionGenealogy>>(`${this.baseUrl}/genealogy/${anchorId}`)
      .pipe(map((response) => response.data));
  }
}
```

### Modèle frontend

```ts
export interface ProductionGenealogy {
  traceabilityLotId?: string;
  traceabilitySourceType?: string;
  rootReceptionId?: string;
  storageUnitId?: string;
  lotNumber?: string;
  storageUnitName?: string;
  filteredQualityControls?: Record<string, string>;
  filtrations?: ProductionFiltrationStep[];
  rootSources?: ProductionRootSource[];
  intakeChain?: ProductionIntakeStep[];
}
```

### Résolution de l'ancre côté UI

```ts
export function genealogyAnchor(ofDetails: Record<string, unknown> | null | undefined): string {
  if (!ofDetails) {
    return '';
  }
  const traceabilityLotId = ofDetails['traceabilityLotId'];
  const lotVracId = ofDetails['lotVracId'];
  return String(traceabilityLotId || lotVracId || '');
}
```

### Lecture

Le frontend applique la même stratégie que le backend :

- d'abord `traceabilityLotId`
- sinon `lotVracId`

---

## 21. Écran de traçabilité filtration

L'écran de filtration recharge la généalogie à partir de la cuve cible ou source.

### Extrait

```ts
const genealogyAnchor = op.target?.id || op.source?.id;
const genealogy$ = genealogyAnchor
  ? this.productionTraceability.getGenealogy(genealogyAnchor).pipe(catchError(() => of(null)))
  : of(null);
```

Pour la saisie QC post-filtration :

```ts
data: {
  filtrationOperationId,
  traceabilityLotId: this.genealogy()?.traceabilityLotId || null
}
```

### Sens

Le frontend exploite le lot métier si disponible pour rattacher les contrôles qualité au bon niveau.

---

## 22. Écran détail OF

### Extrait

```ts
private loadGenealogy(): void {
  const anchorId = this.of?.traceabilityLotId || this.of?.lotVracId;
  if (!anchorId) {
    this.genealogy = null;
    return;
  }

  this.genealogyLoading = true;
  this.productionTraceabilityService.getGenealogy(anchorId).subscribe({
    next: (data) => {
      this.genealogy = data;
      this.genealogyLoading = false;
    }
  });
}
```

### Sens

L'OF se relie à la généalogie matière via son ancre de traçabilité.

---

## 23. Écran détail étiquette

### Extrait

```ts
private loadCurrentGenealogy(label: LabelContentDto): void {
  const genealogyId = label.traceabilityLotId || label.lotId;
  if (!genealogyId) {
    this.currentGenealogy = null;
    return;
  }

  this.productionTraceabilityService.getGenealogy(genealogyId)
    .subscribe({
      next: (genealogy) => {
        this.currentGenealogy = genealogy;
      }
    });
}
```

### Fallback snapshot embarqué

```ts
get filteredLotGenealogy(): ProductionGenealogy | null {
  if (this.currentGenealogy) {
    return this.currentGenealogy;
  }

  const genealogy = this.filteredLotSnapshot?.['genealogy'];
  return genealogy && typeof genealogy === 'object' ? genealogy as ProductionGenealogy : null;
}
```

### Sens

L'étiquette peut :

- recharger la généalogie live
- ou utiliser son snapshot embarqué si nécessaire

---

## 24. Écran projet / expédition

Le frontend affiche la vue globale via la timeline.

### Chargement projet

```ts
loadTraceability(): void {
  if (!this.projectId) return;
  this.expeditionService.getProjectTraceability(this.projectId).subscribe({
    next: (data) => {
      this.traceabilityData = data;
      this.loading = false;
    }
  });
}
```

### Timeline

```ts
eventsForOf(ofId: string): TraceabilityEvent[] {
  const chain = eventChainFor(this.traceabilityData, ofId);
  if (!chain?.events?.length) {
    return [];
  }
  return [...chain.events].sort((a, b) => (a.sequence ?? 0) - (b.sequence ?? 0));
}
```

### Sens

Le frontend n'invente pas la chaîne.  
Il consomme la structure reconstruite côté backend et la présente comme une chronologie exploitable.

---

## 25. Ce que le système fait réellement

### Résumé exact

1. Une réception alimente une cuve via des transactions.
2. Si nécessaire, un lot de traçabilité racine est dérivé de cette cuve.
3. Une filtration termine en créant un nouveau lot de traçabilité enfant.
4. La généalogie est reconstruite à partir de ce lot enfant puis en remontant vers ses parents.
5. Les OF récupèrent et stockent cette ancre de traçabilité.
6. Les étiquettes récupèrent la même ancre et embarquent des snapshots de preuve.
7. Les expéditions regroupent OF, généalogie et étiquettes par ancre.
8. À la validation de l'expédition, un snapshot figé est persisté.

---

## 26. Ce que le système ne garantit pas encore parfaitement

### 1. Hybridation legacy / nouveau modèle

À plusieurs endroits, si `traceabilityLotId` n'est pas trouvé, le code retombe sur `lotVracId` ou `lotId`.

Exemple :

```java
return lotVracId;
```

et :

```java
return lotId;
```

Donc, la migration vers une ancre strictement immuable n'est pas totalement finalisée.

### 2. Création paresseuse

Le lot racine est créé à la demande.  
Cela fonctionne, mais signifie que certaines anciennes données ne sont complètes qu'après usage.

### 3. Scripts DB manuels

Le schéma SQL est présent, mais son exécution n'est pas encore clairement automatisée dans le runtime.

---

## 27. Conclusion

Le mécanisme de traçabilité repose sur une idée simple :

**remplacer la dépendance à l'état mutable des cuves par une chaîne immuable de lots de traçabilité.**

Le coeur du système est :

- `TraceabilityLot` pour représenter la généalogie stable
- `GenealogyService` pour reconstruire la chaîne complète
- `traceabilityLotId` pour transporter cette ancre métier dans `osm-cond`
- les snapshots d'étiquettes et d'expédition pour figer la preuve

Le système fonctionne donc comme une **colonne vertébrale de généalogie métier** traversant :

- la production
- la filtration
- le conditionnement
- l'étiquetage
- l'expédition

Le document de synthèse est désormais dans ce fichier.
