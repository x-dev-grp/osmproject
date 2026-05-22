-- Seed for osmproduction
-- Usage:
--   psql -U postgres -d osmproduction -f "F:/OSM PROJECT/seed-osmproduction.sql"

\set ON_ERROR_STOP on

BEGIN;

INSERT INTO storage_unit (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    name, lot_number, quality_grade, location, description, max_capacity, current_volume,
    next_maintenance_date, last_inspection_date, avg_cost, total_cost, status, last_fill_date,
    last_empty_date, paid_storage, monthly_rental_price, filtered_oil, last_filtration_date
) VALUES
(
    '41000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000131',
    'Tank Source Brut 01', 'LOT-BRUT-001', 'EXTRA_VIRGIN', 'Atelier Production', 'Cuve source avant filtration',
    5000, 3200, '2026-07-01 08:00:00', '2026-05-20 08:00:00', 6.5, 20800,
    'AVAILABLE', '2026-05-20 08:30:00', null, false, 0, false, null
),
(
    '41000000-0000-0000-0000-000000000002', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000132',
    'Tank Filtre 01', 'FI-TEST-001', 'EXTRA_VIRGIN', 'Atelier Production', 'Cuve cible apres filtration',
    3000, 1500, '2026-07-05 08:00:00', '2026-05-21 08:00:00', 6.7, 10050,
    'AVAILABLE', '2026-05-21 08:30:00', null, false, 0, true, '2026-05-21 08:30:00'
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    lot_number = EXCLUDED.lot_number,
    quality_grade = EXCLUDED.quality_grade,
    location = EXCLUDED.location,
    max_capacity = EXCLUDED.max_capacity,
    current_volume = EXCLUDED.current_volume,
    avg_cost = EXCLUDED.avg_cost,
    total_cost = EXCLUDED.total_cost,
    status = EXCLUDED.status,
    filtered_oil = EXCLUDED.filtered_oil,
    last_filtration_date = EXCLUDED.last_filtration_date,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

INSERT INTO filtration_operation (
    id, tenant_id, is_deleted, created_by, created_date, last_modified_by, last_modified_date, external_id,
    source_storage_unit_id, status, operation_date, volume_to_filter, volume_after, loss_volume, loss_percent,
    note, target_storage_unit_id, source_lot_number, target_lot_number
) VALUES
(
    '42000000-0000-0000-0000-000000000001', '4b322fea-6825-4c4c-9534-021cd150d112', false,
    'seed-script', '2026-05-21 09:00:00', 'seed-script', '2026-05-21 09:00:00', '90000000-0000-0000-0000-000000000141',
    '41000000-0000-0000-0000-000000000001', 'COMPLETED', '2026-05-21 08:30:00', 1600, 1500, 100, 6.25,
    'Filtration seed lot pour OF projet', '41000000-0000-0000-0000-000000000002', 'LOT-BRUT-001', 'FI-TEST-001'
)
ON CONFLICT (id) DO UPDATE SET
    source_storage_unit_id = EXCLUDED.source_storage_unit_id,
    status = EXCLUDED.status,
    operation_date = EXCLUDED.operation_date,
    volume_to_filter = EXCLUDED.volume_to_filter,
    volume_after = EXCLUDED.volume_after,
    loss_volume = EXCLUDED.loss_volume,
    loss_percent = EXCLUDED.loss_percent,
    note = EXCLUDED.note,
    target_storage_unit_id = EXCLUDED.target_storage_unit_id,
    source_lot_number = EXCLUDED.source_lot_number,
    target_lot_number = EXCLUDED.target_lot_number,
    last_modified_by = EXCLUDED.last_modified_by,
    last_modified_date = EXCLUDED.last_modified_date;

COMMIT;
