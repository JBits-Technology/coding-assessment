# TypeScript Assessment — Loan Ledger

![TypeScript](https://img.shields.io/badge/TypeScript-blue) ![45 min](https://img.shields.io/badge/⏱-45%20min-lightgrey) ![No external libs](https://img.shields.io/badge/no%20external%20libs-green) ![Medium](https://img.shields.io/badge/difficulty-medium-orange)

You are building the core of a loan management system for a borrower. The focus is on **clean class design and encapsulation** — model real-world loan behaviour using well-defined classes with clear responsibilities.

---

## Context

A borrower takes out a loan (disbursement) and makes repayments over time. Each event is recorded as a transaction. The ledger must always reflect the current outstanding balance and provide a full statement of activity.

---

## Classes to implement

### `LoanTransaction`

Represents a single event on the loan account.

```ts
type LoanTransactionType = "DISBURSEMENT" | "REPAYMENT";

class LoanTransaction {
  readonly id: string;
  readonly type: LoanTransactionType;
  readonly amount: number;
  readonly createdAt: Date;
  note: string | null;

  constructor(
    id: string,
    type: LoanTransactionType,
    amount: number,
    note?: string,
  );
}
```

---

### `LoanAccount`

Encapsulates all loan state. The internal transaction list must **not** be directly accessible — expose it only through the public methods below.

```ts
class LoanAccount {
  private readonly loanRef: string; // e.g. "LOAN-001"
  private readonly borrowerName: string; // e.g. "Alice"
  private readonly transactions: LoanTransaction[]; // internal ledger — never expose directly
  private counter: number; // increments on each new transaction to produce
  // unique IDs: TXN-001, TXN-002, TXN-003 ...

  constructor(loanRef: string, borrowerName: string);

  disburse(amount: number, note?: string): LoanTransaction;
  repay(amount: number, note?: string): LoanTransaction;
  undoLast(): void;

  get balance(): number;
  get totalDisbursed(): number;
  get totalRepaid(): number;

  statement(): string[];
}
```

---

## Balance rules

| Property         | Definition                                                       |
| ---------------- | ---------------------------------------------------------------- |
| `balance`        | Total disbursed minus total repaid. The outstanding amount owed. |
| `totalDisbursed` | Sum of all `DISBURSEMENT` transactions.                          |
| `totalRepaid`    | Sum of all `REPAYMENT` transactions.                             |

All three must be **computed** from the internal transaction list — not stored as mutable counters updated ad hoc.

---

## Method contracts

| Method             | Behaviour                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `disburse(amount)` | Record a disbursement. Appends a `DISBURSEMENT` transaction. Throws if `amount <= 0`.                                         |
| `repay(amount)`    | Record a repayment. Appends a `REPAYMENT` transaction. Throws if `amount <= 0`. Throws if `amount` exceeds current `balance`. |
| `undoLast()`       | Remove the most recently appended transaction. No-op if the ledger is empty.                                                  |
| `statement()`      | Return a formatted string array — one line per transaction with a running balance (see format below).                         |

#### `statement()` line format

```
TXN-001  DISBURSEMENT  +50000.00   balance: 50000.00
TXN-002  REPAYMENT     -10000.00   balance: 40000.00
TXN-003  REPAYMENT     - 5000.00   balance: 35000.00
```

---

## Example usage

```ts
const loan = new LoanAccount("LOAN-001", "Alice");

loan.disburse(50_000, "Initial disbursement");
loan.repay(10_000, "Month 1");
loan.repay(5_000, "Month 2");
loan.disburse(20_000, "Top-up");

console.log(loan.balance); // 55000
console.log(loan.totalDisbursed); // 70000
console.log(loan.totalRepaid); // 15000

loan.undoLast(); // removes the top-up disbursement

console.log(loan.balance); // 35000

try {
  loan.repay(40_000); // throws — exceeds balance of 35000
} catch (e: any) {
  console.log(e.message); // "Repayment exceeds outstanding balance"
}

console.log(loan.statement());
// [
//   "TXN-001  DISBURSEMENT  +50000.00   balance: 50000.00",
//   "TXN-002  REPAYMENT     -10000.00   balance: 40000.00",
//   "TXN-003  REPAYMENT     - 5000.00   balance: 35000.00"
// ]
```

---

## Requirements

- `LoanAccount` must **not** expose its internal transaction list directly — no public array property.
- `balance`, `totalDisbursed`, and `totalRepaid` must be computed from the transaction list, not stored as separate mutable counters.
- All transaction IDs must be unique. Use the provided `counter` to generate them in the format `TXN-001`, `TXN-002`, etc.
- `undoLast()` must also decrement the `counter` so the next transaction reuses the same ID slot.
- `repay()` must validate against the current `balance` before appending.
- `statement()` must compute a running balance in a single forward pass over the transaction list.

---

## Edge cases

| Scenario                               | Expected behaviour                                      |
| -------------------------------------- | ------------------------------------------------------- |
| `repay` with amount > balance          | Throw `Error("Repayment exceeds outstanding balance")`. |
| `disburse` or `repay` with amount <= 0 | Throw `Error("Amount must be greater than zero")`.      |
| `undoLast()` on empty ledger           | No-op — do not throw.                                   |
| `balance` on empty ledger              | Return `0`.                                             |
| `statement()` on empty ledger          | Return `[]`.                                            |

> **Note:** No external libraries. Standard TypeScript only. Submit a single `.ts` file with both classes and the example usage above executed at the bottom.

---

## What we are looking for

- **Encapsulation** — internal state is hidden; the public interface is the only way in.
- **Single responsibility** — `LoanTransaction` owns its data; `LoanAccount` owns business rules.
- **Guard clauses** — validation at the boundary before any state change.
- **Computed properties** — balances derived from the transaction list, not tracked separately.

---

## Follow-up discussion

Be ready to discuss after submission:

1. `balance`, `totalDisbursed`, and `totalRepaid` each traverse the full transaction list. How would you optimise this without breaking encapsulation?
2. `undoLast()` removes the last transaction. How would you extend this into a full undo/redo system?
3. How would you modify `LoanAccount` to support multiple disbursements with different interest rates, while keeping `balance` accurate?
