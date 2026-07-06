# OOP DSA — Linked List Browser History

![TypeScript](https://img.shields.io/badge/TypeScript-blue) ![30 min](https://img.shields.io/badge/⏱-45%20min-lightgrey) ![No external libs](https://img.shields.io/badge/no%20external%20libs-green) ![Medium](https://img.shields.io/badge/difficulty-medium-orange)

Model a browser's back/forward history using a **doubly linked list**. You must implement the list yourself — no arrays, no built-in collections as the underlying store.

---

## Classes to implement

### `HistoryNode`

A single node in the doubly linked list.

```ts
class HistoryNode {
  url: string;
  prev: HistoryNode | null;
  next: HistoryNode | null;

  constructor(url: string);
}
```

---

### `BrowserHistory`

Manages navigation using a doubly linked list internally.

```ts
class BrowserHistory {
  constructor(homepage: string);

  visit(url: string): void;
  back(steps: number): string;
  forward(steps: number): string;
  current(): string;
  history(): string[];
}
```

#### Method contracts

| Method           | Behaviour                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| `visit(url)`     | Navigate to a new URL. **Truncates** all forward history from the current position.                               |
| `back(steps)`    | Move back up to `steps` nodes. Stop at the first node if steps exceed history depth. Returns the URL landed on.   |
| `forward(steps)` | Move forward up to `steps` nodes. Stop at the last node if steps exceed forward depth. Returns the URL landed on. |
| `current()`      | Return the URL at the current pointer position.                                                                   |
| `history()`      | Return all URLs from first to last node (the full list), with the current URL wrapped in `[brackets]`.            |

---

## Example usage

```ts
const b = new BrowserHistory("google.com");

b.visit("github.com");
b.visit("docs.github.com");
b.visit("npmjs.com");

b.back(2); // "github.com"
b.current(); // "github.com"

b.visit("typescript.org");
// forward history (docs.github.com, npmjs.com) is now truncated

b.back(1); // "google.com"  — only 1 step available from github.com? No:
// back(1) from typescript.org → github.com
b.forward(5); // "typescript.org" — clamps at end

b.history();
// ["google.com", "github.com", "[typescript.org]"]
```

---

## Step-by-step trace

```
start              →  google.com
visit("github.com")        →  google.com  ↔  github.com
visit("docs.github.com")   →  google.com  ↔  github.com  ↔  docs.github.com
visit("npmjs.com")         →  google.com  ↔  github.com  ↔  docs.github.com  ↔  npmjs.com
back(2)                    →  google.com  ↔ [github.com] ↔  docs.github.com  ↔  npmjs.com
visit("typescript.org")    →  google.com  ↔  github.com  ↔ [typescript.org]
                              (docs.github.com and npmjs.com are truncated)
back(1)                    →  google.com  ↔ [github.com] ↔  typescript.org
forward(5)                 →  google.com  ↔  github.com  ↔ [typescript.org]
history()                  →  ["google.com", "github.com", "[typescript.org]"]
```

---

## Requirements

- `BrowserHistory` must use `HistoryNode` as its internal structure — no arrays or maps as the primary store.
- `back` and `forward` must clamp silently — never throw when steps exceed available nodes.
- `visit` must sever and discard all nodes ahead of the current pointer.
- `history()` must reflect the live list state after truncation, not a log of all URLs ever visited.
- All pointer manipulation must be done via `prev` / `next` references, not index arithmetic.

---

## Complexity targets

| Operation                | Target |
| ------------------------ | ------ |
| `visit`                  | O(1)   |
| `back(k)` / `forward(k)` | O(k)   |
| `current`                | O(1)   |
| `history`                | O(n)   |

---

## Edge cases

| Scenario                 | Expected behaviour                             |
| ------------------------ | ---------------------------------------------- |
| `back` beyond the start  | Clamp at the first node, return its URL.       |
| `forward` beyond the end | Clamp at the last node, return its URL.        |
| `visit` after `back`     | Truncates all forward nodes before inserting.  |
| `back(0)` / `forward(0)` | Stay in place, return `current()`.             |
| Single-node history      | `back` and `forward` both return the homepage. |

> **Note:** No external libraries. Standard TypeScript only. Submit a single `.ts` file with both classes and the example usage above executed at the bottom.

---

## Follow-up discussion

Be ready to discuss after submission:

1. Why is a doubly linked list a better fit here than a singly linked list or an array?
2. `visit` truncates forward history — walk through the pointer reassignments needed to avoid a memory leak.
3. How would you extend this to support **named snapshots** (bookmarks) that can restore a specific node by name in O(1)?
