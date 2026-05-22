-- Seed for abiooc_inventory
-- Usage:
--   psql -U postgres -d abiooc_inventory -f "F:/OSM PROJECT/seed-abiooc_inventory.sql"

\set ON_ERROR_STOP on

BEGIN;

INSERT INTO emplacements_stock (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    code, nom, type_emplacement, capacite_maximale, capacite_actuelle, zone, disponible, reserve_pour,
    conditions_speciales, temperature_min, temperature_max, description, notes, actif, categorie_article_stocke
) VALUES
(
    '20000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000001',
    'EMP-EMB-01', 'Zone emballages 01', 'ZONE_SECURISEE', '10000', '4500', 'ZONE_EMBALLAGE', true, null,
    'Sec et tempere', 15, 25, 'Zone principale emballages et composants', 'Seed stock packaging', true, 'EMBALLAGE'
),
(
    '20000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000002',
    'EMP-CONS-01', 'Zone consommables 01', 'ZONE_CONTROLE', '5000', '1200', 'ZONE_CONSOMMABLE', true, null,
    'Controle standard', 15, 25, 'Zone etiquettes et consommables', 'Seed stock consumables', true, 'CONSOMMABLE'
),
(
    '20000000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000003',
    'EMP-EXP-01', 'Quai expedition 01', 'QUAI_EXPEDITION', '3000', '0', 'ZONE_EXPEDITION', true, null,
    'Preparation expedition', 15, 25, 'Quai de sortie pour expedition projets', 'Seed expedition dock', true, 'PALETTE'
)
ON CONFLICT (id) DO UPDATE SET
    nom = EXCLUDED.nom,
    type_emplacement = EXCLUDED.type_emplacement,
    capacite_maximale = EXCLUDED.capacite_maximale,
    capacite_actuelle = EXCLUDED.capacite_actuelle,
    zone = EXCLUDED.zone,
    disponible = EXCLUDED.disponible,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO lignes_conditionnement (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    code, nom, description, etat, vitesse_nominale, temps_preparation, temps_nettoyage, responsable,
    date_derniere_maintenance, date_prochaine_maintenance, notes, actif
) VALUES
(
    '21000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000011',
    'LC-01', 'Ligne conditionnement 01', 'Ligne principale bouteille 500ml', 'ACTIF', 1800, 30, 25, 'Chef Ligne A',
    '2026-05-01 08:00:00', '2026-06-01 08:00:00', 'Seed line for OF tests', true
),
(
    '21000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000012',
    'LC-02', 'Ligne conditionnement 02', 'Ligne secondaire renfort test', 'ACTIF', 1200, 20, 20, 'Chef Ligne B',
    '2026-05-03 08:00:00', '2026-06-03 08:00:00', 'Optional backup line', true
)
ON CONFLICT (id) DO UPDATE SET
    nom = EXCLUDED.nom,
    description = EXCLUDED.description,
    etat = EXCLUDED.etat,
    vitesse_nominale = EXCLUDED.vitesse_nominale,
    actif = EXCLUDED.actif,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO skus (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    name, code, type, category, unit_of_measure, description, grade, origin, harvest_campaign,
    volume, packaging_type, barcode, unites_par_cols, colis_par_palette, net_weight, gross_weight,
    brand, density, storage_unit, actif
) VALUES
(
    '22000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000021',
    'Huile Olive Extra Vierge 500ml', 'SKU-EVOO-500', 'NON_VRAC', 'OLIVE_OIL', 'UNITE',
    'SKU test pour conditionnement 500ml', 'EXTRA_VIERGE', 'Tunisie', '2025/2026',
    500, 'BOUTEILLE_VERRE', '6190000000011', 12, 64, 0.46, 0.82,
    'OSM Test', 0.91, 'TANK-FI-01', true
),
(
    '22000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000022',
    'Huile Olive Vrac Filtree', 'SKU-VRAC-FI', 'VRAC', 'OLIVE_OIL', 'LITRE',
    'SKU vrac pour lot filtre de test', 'EXTRA_VIERGE', 'Tunisie', '2025/2026',
    1000, 'VRAC', '6190000000097', null, null, 1.0, 1.0,
    'OSM Test', 0.91, 'TANK-FI-01', true
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    type = EXCLUDED.type,
    volume = EXCLUDED.volume,
    packaging_type = EXCLUDED.packaging_type,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO articles_secs (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    nom, categorie, stock_minimum, stock_maximum, actif, um, sku_id, lot_created_date, lot_ddm, configuration
) VALUES
(
    '23000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000031',
    'Bouteille verre 500ml', 'UNITE', 500, 12000, true, 'UNITE', '22000000-0000-0000-0000-000000000001',
    '2026-05-21 09:00:00', '2028-05-21',
    '{"configType":"UNITE","material":"VERRE","volumeMl":500,"color":"Vert","neckType":"PP31.5","weightGr":320}'::jsonb
),
(
    '23000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000032',
    'Capsule PP31.5', 'EMBALLAGE', 500, 12000, true, 'UNITE', null,
    '2026-05-21 09:00:00', '2028-05-21',
    '{"configType":"EMBALLAGE","sousType":"CAPSULE","material":"ALUMINIUM","dimensions":{"length":3.2,"width":3.2,"height":1.8},"clientBranding":true,"poidsGrammes":2.5}'::jsonb
),
(
    '23000000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000033',
    'Etiquette facade 500ml', 'CONSOMMABLE', 500, 12000, true, 'UNITE', null,
    '2026-05-21 09:00:00', '2028-05-21',
    '{"configType":"CONSOMMABLE","sousType":"ETIQUETTE","usage":"ETIQUETAGE","unit":"piece","quantity":1.0,"temperatureStockageCelsius":22}'::jsonb
),
(
    '23000000-0000-0000-0000-000000000004', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000034',
    'Carton 12x500ml', 'COLIS', 100, 2000, true, 'UNITE', null,
    '2026-05-21 09:00:00', '2028-05-21',
    '{"configType":"COLIS","unitArticleId":"23000000-0000-0000-0000-000000000001","unitsPerColis":12,"dimensions":{"length":40.0,"width":28.0,"height":32.0},"maxWeightKg":8.5}'::jsonb
),
(
    '23000000-0000-0000-0000-000000000005', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000035',
    'Palette europe carton 12x500ml', 'PALETTE', 20, 500, true, 'UNITE', null,
    '2026-05-21 09:00:00', '2028-05-21',
    '{"configType":"PALETTE","type":"EURO","material":"BOIS","colisPerLayer":8,"numberOfLayers":8,"maxHeightCm":180,"clientSpecific":false,"colisId":"23000000-0000-0000-0000-000000000004"}'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
    nom = EXCLUDED.nom,
    categorie = EXCLUDED.categorie,
    stock_minimum = EXCLUDED.stock_minimum,
    stock_maximum = EXCLUDED.stock_maximum,
    actif = EXCLUDED.actif,
    um = EXCLUDED.um,
    sku_id = EXCLUDED.sku_id,
    configuration = EXCLUDED.configuration,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO bom (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    sku_id, version
) VALUES
(
    '24000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000041',
    '22000000-0000-0000-0000-000000000001', 'V1'
)
ON CONFLICT (id) DO UPDATE SET
    sku_id = EXCLUDED.sku_id,
    version = EXCLUDED.version,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO bom_line (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    bom_id, article_sec_id, quantity, unit_of_measure
) VALUES
(
    '24100000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000051',
    '24000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000001', 1.0, 'UNITE'
),
(
    '24100000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000052',
    '24000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000002', 1.0, 'UNITE'
),
(
    '24100000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000053',
    '24000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000003', 1.0, 'UNITE'
),
(
    '24100000-0000-0000-0000-000000000004', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000054',
    '24000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000004', 1.0, 'UNITE'
)
ON CONFLICT (id) DO UPDATE SET
    bom_id = EXCLUDED.bom_id,
    article_sec_id = EXCLUDED.article_sec_id,
    quantity = EXCLUDED.quantity,
    unit_of_measure = EXCLUDED.unit_of_measure,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO stocks_secs (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    article_id, quantite_actuelle, emplacement_id, reserve_pour, reserve_date, quantite_reservee, quantite_disponible
) VALUES
(
    '25000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000061',
    '23000000-0000-0000-0000-000000000001', 5000, '20000000-0000-0000-0000-000000000001',
    'PROJET PRJ-TEST-001', '2026-05-21 09:00:00', 1200, 3800
),
(
    '25000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000062',
    '23000000-0000-0000-0000-000000000002', 5000, '20000000-0000-0000-0000-000000000001',
    'PROJET PRJ-TEST-001', '2026-05-21 09:00:00', 1200, 3800
),
(
    '25000000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000063',
    '23000000-0000-0000-0000-000000000003', 5000, '20000000-0000-0000-0000-000000000002',
    'PROJET PRJ-TEST-001', '2026-05-21 09:00:00', 1200, 3800
),
(
    '25000000-0000-0000-0000-000000000004', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000064',
    '23000000-0000-0000-0000-000000000004', 1500, '20000000-0000-0000-0000-000000000001',
    'PROJET PRJ-TEST-001', '2026-05-21 09:00:00', 1200, 300
),
(
    '25000000-0000-0000-0000-000000000005', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000065',
    '23000000-0000-0000-0000-000000000005', 200, '20000000-0000-0000-0000-000000000003',
    null, null, 0, 200
)
ON CONFLICT (id) DO UPDATE SET
    quantite_actuelle = EXCLUDED.quantite_actuelle,
    emplacement_id = EXCLUDED.emplacement_id,
    reserve_pour = EXCLUDED.reserve_pour,
    reserve_date = EXCLUDED.reserve_date,
    quantite_reservee = EXCLUDED.quantite_reservee,
    quantite_disponible = EXCLUDED.quantite_disponible,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

COMMIT;
