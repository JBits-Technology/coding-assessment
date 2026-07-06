# TypeScript Assessment — Transaction Processor

![TypeScript](https://img.shields.io/badge/TypeScript-blue) ![60 min](https://img.shields.io/badge/⏱-60%20min-lightgrey) ![No external libs](https://img.shields.io/badge/no%20external%20libs-green) ![Medium](https://img.shields.io/badge/difficulty-medium-orange)

You are building the core of a bank account transaction processor. The focus is on **clean class design and encapsulation** — how you model state, enforce business rules, and expose a safe public interface matters as much as correctness.

---

## Context

A customer holds a bank account. They can credit funds, debit funds, and place a **hold** on an amount (e.g. a pending card authorisation). A held amount reduces the available balance but does not leave the account until the hold is either **captured** (confirmed) or **released** (cancelled).

---

## Classes to implement

### `Transaction`

Represents a single transaction on the account.

```ts
type TransactionStatus = "POSTED" | "HELD" | "REVERSED";
type TransactionType = "CREDIT" | "DEBIT" | "HOLD" | "CAPTURE" | "RELEASE";

class Transaction {
  readonly id: string;
  readonly type: TransactionType;
  readonly amount: number;
  readonly createdAt: Date;
  status: TransactionStatus;
  note: string | null;

  constructor(id: string, type: TransactionType, amount: number, note?: string);
}
```

---

### `Account`

Encapsulates all account state. Internal transaction history must **not** be directly accessible — expose it only through the public methods below.

```ts
class Account {
  private readonly accountNumber: string; // e.g. "ACC-001"
  private readonly ownerName: string; // e.g. "Alice"
  private readonly transactions: Transaction[]; // the internal ledger — never expose directly
  private counter: number; // increments on each new transaction to produce
  // unique IDs: TXN-001, TXN-002, TXN-003 ...

  constructor(accountNumber: string, ownerName: string, openingBalance: number);

  credit(amount: number, note?: string): Transaction;
  debit(amount: number, note?: string): Transaction;
  hold(amount: number, note?: string): Transaction;
  capture(holdId: string): Transaction;
  release(holdId: string): Transaction;
  reverse(transactionId: string): Transaction;

  get ledgerBalance(): number;
  get availableBalance(): number;
  get pendingHolds(): number;

  statement(from?: Date, to?: Date): Transaction[];
}
```

---

## Balance rules

| Balance            | Definition                                                                                |
| ------------------ | ----------------------------------------------------------------------------------------- |
| `ledgerBalance`    | Sum of all `POSTED` credits minus all `POSTED` debits. Does **not** include held amounts. |
| `availableBalance` | `ledgerBalance` minus all active hold amounts. This is what the customer can spend.       |
| `pendingHolds`     | Total amount currently under active holds.                                                |

---

## Method contracts

| Method                   | Behaviour                                                                                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `credit(amount)`         | Post a credit. Appends a `POSTED` `CREDIT` transaction. Throws if `amount <= 0`.                                                                                                                       |
| `debit(amount)`          | Post a debit. Throws if `amount <= 0`. Throws if `amount` exceeds `availableBalance`.                                                                                                                  |
| `hold(amount)`           | Place a hold. Appends a `HELD` `HOLD` transaction. Reduces `availableBalance` immediately. Throws if `amount` exceeds `availableBalance`.                                                              |
| `capture(holdId)`        | Settle a hold. Marks the original `HOLD` as `POSTED`, appends a `CAPTURE` transaction. Throws if hold not found or already captured/released.                                                          |
| `release(holdId)`        | Cancel a hold. Marks the original `HOLD` as `REVERSED`, appends a `RELEASE` transaction. Frees the held amount back to `availableBalance`.                                                             |
| `reverse(transactionId)` | Reverse a `POSTED` transaction. Marks it `REVERSED` and posts a counter-transaction (reverses a debit with a credit, and vice versa). Throws if transaction not found, already reversed, or is a hold. |
| `statement(from?, to?)`  | Return all transactions ordered by `createdAt` ascending. If `from`/`to` are provided, filter to that date range (inclusive).                                                                          |

---

## Example usage

```ts
const acc = new Account("ACC-001", "Alice", 100_000);

const t1 = acc.credit(50_000, "Salary");
console.log(acc.ledgerBalance); // 150000
console.log(acc.availableBalance); // 150000

const h1 = acc.hold(30_000, "Hotel authorisation");
console.log(acc.availableBalance); // 120000
console.log(acc.pendingHolds); // 30000

acc.debit(20_000, "Rent");
console.log(acc.ledgerBalance); // 130000
console.log(acc.availableBalance); // 100000

acc.capture(h1.id);
// hold is settled — ledgerBalance decreases by 30000
console.log(acc.ledgerBalance); // 100000
console.log(acc.availableBalance); // 100000
console.log(acc.pendingHolds); // 0

const t2 = acc.debit(10_000, "Groceries");
acc.reverse(t2.id);
// debit is reversed — ledgerBalance restored
console.log(acc.ledgerBalance); // 110000

console.log(acc.statement().length); // 7 transactions total
```

---

## Expected transaction log

After the example above, `acc.statement()` should contain these 7 transactions in order:

```
CREDIT   +100000   POSTED    (opening balance)
CREDIT   + 50000   POSTED    "Salary"
HOLD     + 30000   HELD      "Hotel authorisation"  → status changes to POSTED after capture
DEBIT    - 20000   POSTED    "Rent"
CAPTURE  + 30000   POSTED    (capture of h1)
DEBIT    - 10000   REVERSED  "Groceries"
CREDIT   + 10000   POSTED    (reversal of t2)
```

---

## Requirements

- `Account` must **not** expose its internal transaction list directly — no public array property.
- `ledgerBalance`, `availableBalance`, and `pendingHolds` must be computed from internal state, not stored as mutable fields that are updated ad hoc.
- All transaction IDs must be unique within an account. Use the provided `counter` to generate them in the format `TXN-001`, `TXN-002`, etc.
- The opening balance passed to the constructor must be posted as the first `CREDIT` transaction with note `"Opening balance"`.
- `reverse()` must not be callable on a `HOLD` transaction — holds are cancelled via `release()` only.
- A released or captured hold cannot be captured or released again.
- A reversed transaction cannot be reversed again.

---

## Edge cases

| Scenario                                  | Expected behaviour                                      |
| ----------------------------------------- | ------------------------------------------------------- |
| `debit` exceeds `availableBalance`        | Throw `Error("Insufficient available balance")`.        |
| `hold` exceeds `availableBalance`         | Throw `Error("Insufficient available balance")`.        |
| `capture` on unknown hold ID              | Throw `Error("Hold not found")`.                        |
| `capture` on already captured hold        | Throw `Error("Hold already settled")`.                  |
| `release` on already released hold        | Throw `Error("Hold already released")`.                 |
| `reverse` on a `HOLD` transaction         | Throw `Error("Cannot reverse a hold — use release()")`. |
| `reverse` on already reversed transaction | Throw `Error("Transaction already reversed")`.          |
| `statement()` with no date filters        | Return all transactions.                                |
| `credit` or `debit` with `amount <= 0`    | Throw `Error("Amount must be greater than zero")`.      |

---

## What we are looking for

- **Encapsulation** — internal state is hidden; the public interface is the only way in.
- **Single responsibility** — `Transaction` owns its own data; `Account` owns business rules.
- **Guard clauses** — validation happens at the boundary, not scattered through the logic.
- **Computed properties** — balances are derived from the source of truth (the transaction list), not tracked as separate mutable counters.

> **Note:** No external libraries. Standard TypeScript only. Submit a single `.ts` file with both classes and the example usage above executed at the bottom.

---

## Follow-up discussion

Be ready to discuss after submission:

1. `ledgerBalance` and `availableBalance` traverse the transaction list on every call. At what point does this become a problem, and how would you optimise it without breaking encapsulation?
2. `reverse()` posts a counter-transaction. Should the original transaction's status change to `REVERSED` immediately, or only after the counter-transaction is posted? What real-world event does each model?
3. How would you extend this to support **multi-currency accounts**, where credits and debits can arrive in different currencies and balances are reported in a base currency?
