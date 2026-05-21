# Finance Frontend Enhancement Plan

## Objective
Improve financial correctness, traceability, and resilience across frontend payment flows while keeping compatibility with current backend services (`osm-prod` and `osm-fin`).

## Architecture Context (Current State)

### Backend behavior that FE must respect
- `osm-prod` owns operational payment endpoints:
  - `POST /api/production/oil_sale/payment`
  - `POST /api/production/waste/payment`
  - `POST /api/production/deliveries/payment`
- `osm-prod` updates `paidAmount` / `unpaidAmount` locally, then creates finance entries via Feign (`FinancialTransactionDto`).
- `osm-fin` persists `FinancialTransaction` and supports `transactionType`, `operationType`, `resourceName`, `externalTransactionId`, and payment fields.

### Frontend hotspots
- Models:
  - `src/app/finance/models/financial-transaction.model.ts`
  - `src/app/finance/models/oil-sale.model.ts`
  - `src/app/finance/models/Waste.model.ts`
- Services:
  - `src/app/finance/service/oil-sale.service.ts`
  - `src/app/finance/service/wasteSale.service.ts`
  - `src/app/shared/services/delivery.service.ts`
- Payment UI:
  - `src/app/reception/suppliers/supplier-payment-history/supplier-payment-history.component.ts`
  - `src/app/finance/oil-sales/oil-sale-add/oil-sale-add.component.ts`
  - `src/app/finance/waste/waste-add/waste-add.component.ts`

## Key Risks Identified
- Enum mismatch risk (`cash` vs `CASH`) in FE `PaymentMethod`.
- Untyped `any` payment payloads across services.
- Incomplete waste payload fields (`currency`, `paymentMethod` may be null).
- Inconsistent API response parsing (`data` vs `data[0]`).
- Duplicate submits can create duplicate payments.
- Validation logic duplicated across forms and dialogs.

## Target Contract (Canonical FE Payment Request)
All payment flows must send the same shape:
- `idOperation: string`
- `amount: number`
- `currency: Currency`
- `paymentMethod: PaymentMethod`
- `checkNumber?: string | null`
- `bankAccount?: BankAccount | null`
- `supplier?: SupplierType | null`
- `customer?: unknown | null`

Rules:
- `CHEQUE` requires `checkNumber`.
- `TRANSFER` requires `bankAccount`.
- `amount` must be positive and not exceed remaining unpaid amount unless explicit refund flow is introduced.

## Detailed Implementation Plan

### Phase 1: Contract and enum hardening (highest priority)
1. Add `PaymentRequest` interface under `src/app/finance/models/`.
2. Replace `processPayment(payload:any)` signatures with `processPayment(payload: PaymentRequest)` in:
   - `oil-sale.service.ts`
   - `wasteSale.service.ts`
   - `delivery.service.ts`
3. Normalize `PaymentMethod` values in `financial-transaction.model.ts` to backend-compatible values (`CASH`, `CHEQUE`, `TRANSFER`, ...).
4. Add one mapping helper `mapMoneyMethodToPaymentEnum()` and use it everywhere instead of local switch/ternary blocks.

Acceptance criteria:
- TypeScript compile catches invalid payment payload shape.
- No raw string literals (`cash/check/bank_transfer`) passed directly to APIs.

### Phase 2: Form correctness and validation consistency
1. Update `waste-add.component.ts` form to include required finance fields:
   - `currency` default `TND`
   - `paymentMethod` default `CASH`
2. Add shared validators for payment constraints:
   - positive amount
   - max unpaid guard
   - conditional required fields (`checkNumber`/`bankAccount`)
3. Reuse validators in:
   - `supplier-payment-history.component.ts`
   - waste/oil create and payment flows where applicable.

Acceptance criteria:
- Forms cannot submit invalid payment combinations.
- No null/undefined payment fields for required backend fields.

### Phase 3: Response normalization and robustness
1. Add `normalizeApiData<T>()` helper to unify extraction of `response.data` and `response.data[0]`.
2. Refactor finance components with mixed parsing behavior:
   - `oil-sale-add.component.ts`
   - `transaction-add.component.ts`
   - waste/expense view/edit loaders.
3. Remove direct array indexing assumptions from components.

Acceptance criteria:
- View/edit pages work regardless of single-object or single-item-array response shape.

### Phase 4: Duplicate action prevention and UX reliability
1. Apply submit lock pattern uniformly:
   - disable submit button while request is inflight
   - ignore repeated click/enter submissions
2. Ensure dialog close only after API response for payment actions.
3. Standardize user feedback messages for success/failure with transaction context.

Acceptance criteria:
- Multiple fast clicks produce only one API request.
- Payment result is always explicit to user.

### Phase 5: Financial traceability alignment with backend
1. Ensure FE sends/retains identifiers useful for tracing:
   - `idOperation`
   - operation source context (delivery/oil sale/waste sale) in local state and logs.
2. Confirm backend-created transaction references are surfaced in FE detail views where available.
3. Prepare extension point for idempotency key once backend supports it.

Acceptance criteria:
- Each payment action can be traced from UI action to backend operation id.
- Support/debug teams can follow a payment path without manual DB joins.

## Backend Alignment Notes (for coordinated work)
- `osm-prod` currently performs local state update then finance creation (potential partial failure window).
- `osm-fin` has placeholders for some side-effect methods in `FinancialTransactionService`.
- Recommended next backend step (separate track): enforce idempotency and unique finance reference by `(resourceName, externalTransactionId, operationType, transactionType)`.

## Rollout Strategy
- Use feature branch with small commits per phase.
- Sequence:
  1. Phase 1
  2. Phase 2
  3. Phase 3
  4. Phase 4
  5. Phase 5
- Keep backward compatibility during transition with minimal adapter helpers.

## Verification Plan

### Functional test matrix
- Oil sale:
  - create (cash/cheque/transfer)
  - partial payment
  - full payment
- Waste sale:
  - create with required finance fields
  - payment with each money method
- Delivery payment:
  - purchase/outbound
  - simple reception/inbound
  - exchange path where applicable

### Technical checks
- `npm run build` passes.
- No TypeScript `any` for payment requests in target services.
- API payload snapshots match backend DTO expectations.
- Manual retry/double-click does not duplicate requests.

## Deliverables
- Updated FE models/services/components per phases above.
- Shared utilities:
  - payment method mapper
  - response normalizer
  - payment validators
- Short implementation note documenting contract decisions and edge cases.
