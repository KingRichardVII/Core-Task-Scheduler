# CPU Task Scheduler
## *By Richard Phan*

### Description
#### This is a command-line CPU-style scheduler that reads commands from a text file and simulates how an operating system decides which task should run next.
The program maintains **READY**, **RUNNING**, and **BLOCKED** tasks using fully custom data structures—**no Python dict, set, heapq, or collections**—and prints a trace of all scheduling events exactly as required.

---

### Data Structure Design & Invariants

**Task Objects**
- `Task { id: str, priority: int, remaining: int, insertion_order: int }`
- Each task tracks:
  - `priority` (lower = more important)
  - `remaining` CPU time
  - `insertion_order` to break ties deterministically
- *Invariant:* A task exists in exactly one place: READY heap, BLOCKED queue, or RUNNING slot.

**READY Queue — Min-Heap (Priority Queue)**
- Implemented using:
  - A custom **Vector** (dynamic array)
  - A binary **min-heap** layered over that Vector
- Ordering:
  1. Lower priority value first
  2. If tied, earlier `insertion_order`
- *Invariants:*
  - Heap property holds for all nodes
  - `Vector._size` ≤ `Vector._capacity`
  - Elements only stored in `[0 … size-1]`

**BLOCKED Queue — Circular FIFO Queue**
- Implemented using a manually managed circular array:
  - `_head`, `_tail`, `_size`, `_capacity`
- *Invariant:* Tasks exit in the same order they entered.

**RUNNING Task**
- At most **one** task may be RUNNING at any time.
- When a task finishes (`remaining == 0`), it is removed from the system immediately and no replacement is chosen until the *next* `TICK`.

---

### Scheduling Behavior
- **TICK**
  - Advances time.
  - If no RUNNING task, picks highest-priority READY task.
  - Decrements `remaining`; prints `RUNNING id` or `IDLE`.
  - Finished tasks leave immediately but do **not** trigger an instant replacement.

- **BLOCK / UNBLOCK**
  - `BLOCK` moves RUNNING → BLOCKED (FIFO).
  - `UNBLOCK` moves oldest BLOCKED → READY.
  - Neither command ever preempts the current runner.

- **PRINT_READY / PRINT_BLOCKED / STATUS**
  - Provide formatted snapshots.
  - READY uses **task clones** in a temporary heap to avoid mutating real queue state.
  - All formats follow the exact `-> id | priority=P | remaining=R` specifications.

---

### Run Instructions

**Run in a terminal of your IDE (VS Code, PyCharm, etc.)**

```
python3 main.py commands.txt
```

- Ensure `commands.txt` is in the same directory as `main.py`.
- If the file is missing or unreadable, the program prints:
  `USAGE: <program> <commands_file>`
- The scheduler is **non-interactive**; it processes the entire file and terminates.

---

### Commands

- `ADD_TASK id priority burst_time`
  - Creates a new task unless the id already exists → `DUPLICATE`.
  - Errors: wrong argument count, non-integer values, or non-positive burst time.

- `TICK`
  - Runs the highest-priority READY task for one unit of time.
  - Prints `RUNNING id` or `IDLE`.

- `BLOCK`
  - Moves the RUNNING task into BLOCKED → prints `BLOCKED id`.
  - If no task running → `ERROR: NO_TASK_RUNNING`.

- `UNBLOCK`
  - Moves oldest BLOCKED task to READY → prints `UNBLOCKED id`.
  - If none blocked → `ERROR: NO_TASK_BLOCKED`.

- `PRINT_READY`
  - Shows READY queue in the order tasks would run.
  - Prints `EMPTY` if none.

- `PRINT_BLOCKED`
  - Shows BLOCKED queue in FIFO order or `EMPTY`.

- `STATUS`
  - Shows current RUNNING task or `IDLE`.

- `QUIT`
  - Stops the scheduler immediately; lines after `QUIT` are ignored.

---

## Test Transcript
Please see `commands.txt` and `edge_cases.txt` for representative scenarios showing task creation, blocking/unblocking, finishing, and queue printing.
