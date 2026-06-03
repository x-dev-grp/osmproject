# Manual Test Data - Reception To Expedition

Date baseline: May 30, 2026

## 1) Master Data (create once)

### A. Region / Parcel
- Region name: `SFAX_NORD`
- Parcel name: `PARCELLE_A1`

### B. Reception Supplier
Screen: `/reception/fournisseur/new`
- Name: `Ben Youssef`
- Lastname: `Trading`
- Phone: `+21671123456`
- Matricule fiscal: `MF-TEST-001`
- Region: `SFAX_NORD`
- Supplier type: `AGRICULTEUR`
- RIB: `TN5914207207100707129648`
- Bank: `BNA`

### C. Packaging Stock Supplier (if needed)
Screen: `/stock/fournisseurs/nouveau`
- Nom: `PackLab Tunisie`
- Contact: `+21671222333`

### D. Stock Emplacements
Screen: `/stock/emplacements/nouveau`
1. Packaging zone
- Nom: `Zone emballage test`
- Type emplacement: `ZONE_SECURISEE`
- Categorie article stocke: `EMBALLAGE`
- Capacite maximale: `10000`
- Capacite actuelle: `0`
- Zone: `ZONE_EMBALLAGE`
- Disponible: `true`

2. Expedition dock
- Nom: `Quai expedition test`
- Type emplacement: `QUAI_EXPEDITION`
- Categorie article stocke: `PALETTE`
- Capacite maximale: `3000`
- Capacite actuelle: `0`
- Zone: `ZONE_EXPEDITION`
- Disponible: `true`

### E. Conditioning Line
Screen: `/stock/lignes/nouveau`
- Nom: `Ligne conditionnement test 01`
- Description: `Ligne 500ml`
- Etat: `ACTIF`
- Vitesse nominale: `1800`
- Temps preparation: `30`
- Temps nettoyage: `25`
- Responsable: `Chef Ligne Test`

### F. Articles (for BOM)
Screen: `/stock/articles/nouveau`

1. Unite
- Nom: `Bouteille verre 500ml test`
- Categorie: `UNITE`
- UM: `UNITE`
- Stock min/max: `500` / `12000`
- Config: material `VERRE`, volume `500`, color `Vert`, neck `PP31.5`, weight `320`

2. Emballage
- Nom: `Capsule PP31.5 test`
- Categorie: `EMBALLAGE`
- UM: `UNITE`
- Stock min/max: `500` / `12000`

3. Consommable
- Nom: `Etiquette facade 500ml test`
- Categorie: `CONSOMMABLE`
- UM: `UNITE`
- Stock min/max: `500` / `12000`

4. Colis
- Nom: `Carton 12x500ml test`
- Categorie: `COLIS`
- UM: `UNITE`
- Stock min/max: `100` / `2000`
- Unit article: `Bouteille verre 500ml test`
- Units/colis: `12`
- Dimensions: `40 x 28 x 32`

5. Palette
- Nom: `Palette europe carton 12x500ml test`
- Categorie: `PALETTE`
- UM: `UNITE`
- Stock min/max: `20` / `500`
- Colis article: `Carton 12x500ml test`
- Colis/layer: `8`
- Layers: `8`

### G. Product (SKU)
Screen: `/stock/products/nouveau`
- Name: `Huile Olive Extra Vierge 500ml Test`
- Type: `NON_VRAC`
- Unit of measure: `BOTTLE`
- Grade: `EXTRA_VIERGE`
- Origin: `Tunisie`
- Harvest campaign: `2025/2026`
- Volume: `500`
- Barcode: `6190000005011`
- Net weight: `0.46`
- Gross weight: `0.82`
- Brand: `OSM Test`

### H. BOM
Screen: `/stock/boms/nouveau`
- Product: `Huile Olive Extra Vierge 500ml Test`
- Active: `true`
- Lines:
  - `Bouteille verre 500ml test` -> `1`
  - `Capsule PP31.5 test` -> `1`
  - `Etiquette facade 500ml test` -> `1`
  - `Carton 12x500ml test` -> `1`

### I. Client
Screen: `/stock/clients/nouveau`
- Nom: `Client Test Distribution`
- Type: `BUYER`
- Email: `client.test@osm.local`
- Telephone: `+21670000000`
- Adresse: `Zone Industrielle 1`
- Ville: `Sfax`
- Pays: `Tunisie`
- Code postal: `3000`
- Private label: `true`
- SIRET: `12345678900011`
- TVA: `TN123456789`

## 2) Reception Data Entry

### A. Olive Reception
Screen: `/reception/reception-olive/olive_purchase`
- Delivery date: `2026-05-30`
- Truck plate: `258TN1234`
- Supplier: `Ben Youssef Trading`
- Region: `SFAX_NORD`
- Parcel: `PARCELLE_A1`
- Olive type: `OB`
- Gross weight: `18500`
- Empty truck weight: `7200`
- Net weight (auto): `11300`
- Sack count: `220`

### B. Oil Reception
Screen: `/reception/reception-huile`
- Delivery date: `2026-05-30`
- Supplier: `Ben Youssef Trading`
- Region: `SFAX_NORD`
- Parcel: `PARCELLE_A1`
- Oil quantity (poidsNet): `1500`
- Oil type: `OB`
- Truck plate: `412TN9087`

## 3) Project Creation
Screen: `/projets/new`
- Client: `Client Test Distribution`
- Type produit: `EXTRA_VIERGE`
- Type emballage: `BOUTEILLE`
- Produit fini: `Huile Olive Extra Vierge 500ml Test`
- BOM: created BOM above
- Ligne(s): `Ligne conditionnement test 01`
- Date limite livraison: `2026-06-15`
- Quantite cible: `1200`
- Unite: `UNITES`
- Prix unitaire: `8.5`
- Conditions livraison: `Livraison palette complete sur rendez-vous`

## 4) OF Creation
Screen: `/of/nouveau`
- Projet: project created above
- Produit fini: `Huile Olive Extra Vierge 500ml Test`
- Nomenclature: active BOM
- Ligne: `Ligne conditionnement test 01`
- Quantite cible: `1200`
- Date debut: `2026-06-01`
- Date fin: `2026-06-02`
- Cuve source (`lotVracId`): optional (set if available)

## 5) Expedition Creation
Screen: `/projets/detail/{projectId}/expedition`

Create form:
- Destination: `Depot Client Sfax`
- Date prevue: `2026-06-15`
- Notes: `Palette complete - test flux E2E`
- Select OF line: created OF
- Quantity: `1200`
- Lot source: `FI-TEST-001` (or OF lot)
- Volume: `3.8`

Logistics update:
- Transporteur: `TransOil TN`
- Chauffeur: `Sami Trabelsi`
- Camion: `215TN5531`
- Tracking: `TRK-EXP-2026-0001`
- Incoterm: `EXW`

Status actions:
1. `READY`
2. `VALIDATE`
3. `SHIP`
4. `DELIVER`
5. `CLOSE`

## 6) Second Expedition (partial shipment test)

Create another project with same data but quantity `600`, then:
- OF quantity: `600`
- Expedition quantity: `300` first shipment
- Second expedition quantity: `300` second shipment

This validates split expedition behavior and remaining quantity checks.
