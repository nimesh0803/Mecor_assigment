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



## Requirements

* Python **3.10+**
* `pytest`

```
pytest>=8.0
```

## Setup

### Windows (PowerShell)

```powershell
cd Mecor_assigment
pip install pytest>=8.0
```

### macOS/Linux

```bash
cd Mecor_assigment
pip install pytest>=8.0
```

## Running tests (single command)

From repo root:

```bash
pytest -q tests
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


## Design choices

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

## Acknowledgment (optional)

Used it for fixing sytanx error 
