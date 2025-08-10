# Mecor_assigment

# Referral Network Challenge — Python

## Overview

Implementation of Parts 1–5:

* **Part 1**: Referral DAG with constraints (no self-referrals, unique parent, acyclic) + direct referrals.
* **Part 2**: Downstream reach count and top-K referrers by reach.
* **Part 3**: Read-only influencer metrics — unique reach expansion (greedy max-coverage) and flow centrality (ancestors×descendants in a forest).
* **Part 4**: Expected-value simulation for fixed initial referrers and capacity; `simulate` and `days_to_target`.
* **Part 5**: Minimum bonus to hit target using a monotone adoption function; binary search over \$10 steps.

## Repo structure

```
your-project/
├─ source/
│  ├─ __init__.py
│  ├─ referral_network.py     # Parts 1–3: core data structure & metrics
│  ├─ simulation.py           # Part 4: expected-value simulation
│  └─ bonus_opt.py            # Part 5: optimization (uses simulation)
└─ tests/
   ├─ test_referral_network.py      # Part 1
   ├─ test_referral_reach.py        # Part 2
   ├─ test_part3_influencers.py     # Part 3
   ├─ test_part4_simulation.py      # Part 4
   └─ test_part5_bonus_opt.py       # Part 5
```

> `bonus_opt.py` imports with `from .simulation import ...`, so keep `source/__init__.py` (can be empty). Tests include a fallback to path-style imports if you prefer `PYTHONPATH=source`.

## Requirements

* Python **3.10+**
* `pytest`

`requirements.txt` (optional):

```
pytest>=8.0
```

## Setup

### Windows (PowerShell)

```powershell
cd your-project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
cd your-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running tests (single command)

From repo root:

```bash
pytest -q
```

If you prefer path-style imports instead of the package:

```powershell
# Windows
$env:PYTHONPATH="source"; pytest -q
```

```bash
# macOS/Linux
export PYTHONPATH=source; pytest -q
```

## Quick sanity check

```bash
python - <<'PY'
from source.referral_network import ReferralNetwork
g = ReferralNetwork()
g.add_referral("A", "B")
g.add_referral("A", "C")
g.add_referral("B", "D")
g.add_referral("C", "E")
print("direct(A)=", g.get_direct_referrals("A"))    # ['B','C']
print("reach(A)=", g.reach_count("A"))              # 4
print("top2=", g.top_k_referrers_by_reach(2))       # [('A',4), ('B',1)] (example)
print("flow=", g.flow_centrality()[:3])             # e.g., [('C',4), ('B',3), ...] depending on graph
PY
```

## Design choices (concise)

* **Graph model**: Directed acyclic forest (unique parent per node).
  `children: Dict[str, Set[str]]`, `parent: Dict[str, str]`, `nodes: Set[str]`.
* **Part 1**: Enforced in `add_referral` — reject self-referrals; enforce unique parent; BFS candidate→referrer to prevent cycles; idempotent edge insert; implicit user creation.
* **Part 2**: `reach_count` via BFS; `top_k` sorts by reach then id. (Memoization possible if needed.)
* **Part 3**:

  * `unique_reach_expansion(k)`: greedy max-coverage on precomputed `reach_set(u)`.
  * `flow_centrality()`: in a forest, `score(v) = ancestors(v) * descendants(v)` using DFS up/down; read-only.
* **Part 4**: Expected value (no RNG). DP builds capped Binomial distribution for one referrer; scale by 100.
* **Part 5**: Monotone `adoption_prob(bonus)`; exponential + binary search over \$10 steps to find minimum bonus hitting target.

## Complexity (big-O)

* `add_referral`: O(V+E) worst-case (cycle-check BFS).
* `get_direct_referrals`: O(d log d) (sorting d children).
* `reach_count`: O(V+E).
* `unique_reach_expansion`: O(k·N) set ops over precomputed reach sets.
* `flow_centrality`: O(N+E) via ancestor/descendant counts (forest).
* `simulate`: O(days·C) (C=10 constant).
* `min_bonus_for_target`: O(log B · days · C) via binary search.

## Assumptions & edge cases

* Graph remains a **forest** (unique parent). Metrics never mutate graph.
* Unknown users → empty lists/zero counts.
* Simulation caps per-referrer successes at 10 and does not promote new referrers.
* `adoption_prob` is monotone non-decreasing in \[0,1].

## Submission

* Private GitHub repo, share with the specified reviewer email.
* Include this README and tests; a single `pytest -q` must work from repo root.

## Acknowledgment (optional)

AI assistance used for scaffolding and documentation.
