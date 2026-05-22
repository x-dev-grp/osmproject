-- Seed for osmoc
-- Usage:
--   psql -U postgres -d osmoc -f "F:/OSM PROJECT/seed-osmoc.sql"

\set ON_ERROR_STOP on

BEGIN;

INSERT INTO clients (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    nom, code_client, type, email, telephone, adresse, ville, pays, code_postal, private_label,
    siret, numero_tva, notes, actif
) VALUES
(
    '31000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000071',
    'Client Test Distribution', 'CLI-TEST-001', 'BUYER', 'client.test@osm.local', '+21670000000',
    'Zone Industrielle 1', 'Sfax', 'Tunisie', '3000', true,
    '12345678900011', 'TN123456789', 'Client seed pour projet et expedition', true
)
ON CONFLICT (id) DO UPDATE SET
    nom = EXCLUDED.nom,
    code_client = EXCLUDED.code_client,
    type = EXCLUDED.type,
    email = EXCLUDED.email,
    telephone = EXCLUDED.telephone,
    private_label = EXCLUDED.private_label,
    actif = EXCLUDED.actif,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO projet (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    code, client_id, type_produit, type_emballage, quantite_cible, unite, date_limite_livraison,
    prix_unitaire, valeur_totale, conditions_livraison, statut
) VALUES
(
    '32000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000081',
    'PRJ-TEST-001', '31000000-0000-0000-0000-000000000001', 'EXTRA_VIERGE', 'BOUTEILLE', 1200, 'UNITE', '2026-06-15',
    8.500, 10200.000, 'Livraison palette complete sur rendez-vous', 'EN_PREPARATION'
)
ON CONFLICT (id) DO UPDATE SET
    code = EXCLUDED.code,
    client_id = EXCLUDED.client_id,
    type_produit = EXCLUDED.type_produit,
    type_emballage = EXCLUDED.type_emballage,
    quantite_cible = EXCLUDED.quantite_cible,
    unite = EXCLUDED.unite,
    date_limite_livraison = EXCLUDED.date_limite_livraison,
    prix_unitaire = EXCLUDED.prix_unitaire,
    valeur_totale = EXCLUDED.valeur_totale,
    statut = EXCLUDED.statut,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO projet_lignes_conditionnement (projet_id, ligne_id) VALUES
('32000000-0000-0000-0000-000000000001', '21000000-0000-0000-0000-000000000001'),
('32000000-0000-0000-0000-000000000001', '21000000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

INSERT INTO projet_produit (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    projet_id, product_id, bom_id, quantite_cible
) VALUES
(
    '33000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000091',
    '32000000-0000-0000-0000-000000000001', '22000000-0000-0000-0000-000000000001',
    '24000000-0000-0000-0000-000000000001', 1200
)
ON CONFLICT (id) DO UPDATE SET
    projet_id = EXCLUDED.projet_id,
    product_id = EXCLUDED.product_id,
    bom_id = EXCLUDED.bom_id,
    quantite_cible = EXCLUDED.quantite_cible,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO projet_reservation (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    projet_id, article_id, quantite_reservee, statut
) VALUES
(
    '34000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000101',
    '32000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000001', 1200, 'CONFIRMED'
),
(
    '34000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000102',
    '32000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000002', 1200, 'CONFIRMED'
),
(
    '34000000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000103',
    '32000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000003', 1200, 'CONFIRMED'
),
(
    '34000000-0000-0000-0000-000000000004', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000104',
    '32000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000004', 1200, 'CONFIRMED'
)
ON CONFLICT (id) DO UPDATE SET
    projet_id = EXCLUDED.projet_id,
    article_id = EXCLUDED.article_id,
    quantite_reservee = EXCLUDED.quantite_reservee,
    statut = EXCLUDED.statut,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO ordre_fabrication (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    code, statut, date_debut_prevue, date_fin_prevue, quantite_cible, quantite_bonne, quantitenc,
    duree_reelle, sku_id, bom_id, ligne_id, lot_vrac_id, motifnc, quality_status, projet_id
) VALUES
(
    '35000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000111',
    'OF-TEST-001', 'PLANIFIE', '2026-05-22 08:00:00', '2026-05-22 16:00:00', 1200, 0, 0,
    null, '22000000-0000-0000-0000-000000000001', '24000000-0000-0000-0000-000000000001',
    '21000000-0000-0000-0000-000000000001', '41000000-0000-0000-0000-000000000002', null, 'FREE',
    '32000000-0000-0000-0000-000000000001'
)
ON CONFLICT (id) DO UPDATE SET
    code = EXCLUDED.code,
    statut = EXCLUDED.statut,
    quantite_cible = EXCLUDED.quantite_cible,
    sku_id = EXCLUDED.sku_id,
    bom_id = EXCLUDED.bom_id,
    ligne_id = EXCLUDED.ligne_id,
    lot_vrac_id = EXCLUDED.lot_vrac_id,
    quality_status = EXCLUDED.quality_status,
    projet_id = EXCLUDED.projet_id,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO ligne_of (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    of_id, article_id, quantite_theorique, quantite_reelle, motif_ajustement
) VALUES
(
    '36000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000121',
    '35000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000001', 1200, null, null
),
(
    '36000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000122',
    '35000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000002', 1200, null, null
),
(
    '36000000-0000-0000-0000-000000000003', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000123',
    '35000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000003', 1200, null, null
),
(
    '36000000-0000-0000-0000-000000000004', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000124',
    '35000000-0000-0000-0000-000000000001', '23000000-0000-0000-0000-000000000004', 1200, null, null
)
ON CONFLICT (id) DO UPDATE SET
    of_id = EXCLUDED.of_id,
    article_id = EXCLUDED.article_id,
    quantite_theorique = EXCLUDED.quantite_theorique,
    quantite_reelle = EXCLUDED.quantite_reelle,
    motif_ajustement = EXCLUDED.motif_ajustement,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

COMMIT;
