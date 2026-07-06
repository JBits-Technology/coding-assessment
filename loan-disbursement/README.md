# OOP DSA — Loan Ledger

![TypeScript](https://img.shields.io/badge/TypeScript-blue) ![45 min](https://img.shields.io/badge/⏱-45%20min-lightgrey) ![No external libs](https://img.shields.io/badge/no%20external%20libs-green) ![Medium](https://img.shields.io/badge/difficulty-medium-orange)

Model a borrower's loan account using a **singly linked list** where each node represents a disbursement or repayment event. You must implement the list yourself — no arrays or built-in collections as the underlying store.

---

## Classes to implement

### `LedgerNode`

A single node in the singly linked list.

```ts
type TransactionType = "DISBURSEMENT" | "REPAYMENT";

class LedgerNode {
  id: number;
  type: TransactionType;
  amount: number;
  next: LedgerNode | null;

  constructor(id: number, type: TransactionType, amount: number);
}
```

---

### `LoanLedger`

Manages the loan lifecycle using `LedgerNode` as its internal structure.

```ts
class LoanLedger {
  constructor(borrowerName: string);

  disburse(amount: number): void;
  repay(amount: number): void;
  balance(): number;
  totalDisbursed(): number;
  totalRepaid(): number;
  undoLast(): void;
  statement(): string[];
}
```

#### Method contracts

| Method             | Behaviour                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| `disburse(amount)` | Append a `DISBURSEMENT` node. Throws if `amount <= 0`.                                                          |
| `repay(amount)`    | Append a `REPAYMENT` node. Throws if `amount <= 0`. Throws if `amount` exceeds the current outstanding balance. |
| `balance()`        | Return total disbursed minus total repaid.                                                                      |
| `totalDisbursed()` | Return the sum of all `DISBURSEMENT` nodes.                                                                     |
| `totalRepaid()`    | Return the sum of all `REPAYMENT` nodes.                                                                        |
| `undoLast()`       | Remove the most recently appended node (tail). No-op if the ledger is empty.                                    |
| `statement()`      | Return a formatted string array — one line per node (see format below).                                         |

#### `statement()` line format

```
#1  DISBURSEMENT  +50000.00   balance: 50000.00
#2  REPAYMENT     -10000.00   balance: 40000.00
#3  REPAYMENT     -5000.00    balance: 35000.00
#4  DISBURSEMENT  +20000.00   balance: 55000.00
```

Each line must include the node's sequential number, type, signed amount (+ for disbursement, − for repayment), and the running balance at that point.

---

## Example usage

```ts
const ledger = new LoanLedger("Alice");

ledger.disburse(50_000);
ledger.repay(10_000);
ledger.repay(5_000);
ledger.disburse(20_000);

console.log(ledger.balance()); // 55000
console.log(ledger.totalDisbursed()); // 70000
console.log(ledger.totalRepaid()); // 15000

ledger.undoLast(); // removes the second DISBURSEMENT

console.log(ledger.balance()); // 35000

ledger.repay(40_000); // throws — exceeds balance of 35000

console.log(ledger.statement());
// [
//   "#1  DISBURSEMENT  +50000.00   balance: 50000.00",
//   "#2  REPAYMENT     -10000.00   balance: 40000.00",
//   "#3  REPAYMENT     -5000.00    balance: 35000.00"
// ]
```

---

## Step-by-step trace

```
disburse(50000)  →  [DISBURSEMENT 50000]
repay(10000)     →  [DISBURSEMENT 50000] → [REPAYMENT 10000]
repay(5000)      →  [DISBURSEMENT 50000] → [REPAYMENT 10000] → [REPAYMENT 5000]
disburse(20000)  →  [DISBURSEMENT 50000] → [REPAYMENT 10000] → [REPAYMENT 5000] → [DISBURSEMENT 20000]
undoLast()       →  [DISBURSEMENT 50000] → [REPAYMENT 10000] → [REPAYMENT 5000]
                     tail is now REPAYMENT 5000
```

---

## Requirements

- `LoanLedger` must use `LedgerNode` as its internal structure — no arrays or maps as the primary store.
- `undoLast()` must traverse to the second-to-last node and sever the tail — O(n).
- `repay()` must validate against the current balance before appending.
- `statement()` must compute a **running balance** per node in a single forward pass.
- All pointer manipulation must be done via `next` references, not index arithmetic.
- Node IDs must be sequential and stable — `undoLast()` must decrement the counter so a re-inserted node reuses the same ID slot.

---

## Complexity targets

| Operation            | Target                                 |
| -------------------- | -------------------------------------- |
| `disburse` / `repay` | O(1) — maintain a tail pointer         |
| `balance`            | O(1) — maintain a running total        |
| `undoLast`           | O(n) — must traverse to second-to-last |
| `statement`          | O(n)                                   |

---

## Edge cases

| Scenario                               | Expected behaviour                                      |
| -------------------------------------- | ------------------------------------------------------- |
| `repay` with amount > balance          | Throw `Error("Repayment exceeds outstanding balance")`. |
| `disburse` or `repay` with amount <= 0 | Throw `Error("Amount must be greater than zero")`.      |
| `undoLast()` on empty ledger           | No-op — do not throw.                                   |
| `undoLast()` on single-node ledger     | Ledger becomes empty; head and tail are both `null`.    |
| `balance()` on empty ledger            | Return `0`.                                             |
| `statement()` on empty ledger          | Return `[]`.                                            |

> **Note:** No external libraries. Standard TypeScript only. Submit a single `.ts` file with both classes and the example usage above executed at the bottom.

---

## Follow-up discussion

Be ready to discuss after submission:

1. You maintain a tail pointer for O(1) append — but `undoLast()` is still O(n). How would you make it O(1), and what data structure would you use?
2. `repay()` validates against the current balance. Where do you store that state — do you recompute it on every call or maintain it incrementally? What are the trade-offs?
3. How would you extend this to support multiple loans per borrower, each with its own ledger, while sharing a single transaction ID sequence across all of them?
