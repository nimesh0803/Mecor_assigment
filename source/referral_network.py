# source/referral_network.py
from collections import defaultdict, deque
from typing import Dict, Set, List

class ReferralNetwork:
    """
    Directed acyclic graph (DAG) with unique parent per node (except roots).
    Constraints enforced on add_referral():
      - no self-referral
      - candidate has at most one referrer
      - adding the edge must not create a cycle
    """
    def __init__(self) -> None:
        self._children: Dict[str, Set[str]] = defaultdict(set)
        self._parent: Dict[str, str] = {}
        self._nodes: Set[str] = set()

    # ---- basic node/edge ops ----
    def add_user(self, user: str) -> None:
        if user not in self._nodes:
            self._nodes.add(user)
            _ = self._children[user]  # ensure key exists

    def add_referral(self, referrer: str, candidate: str) -> bool:
        """
        Returns True if a new edge is added, False if the exact edge already exists.
        Raises ValueError on any constraint violation.
        """
        if referrer == candidate:
            raise ValueError("no self-referrals")

        # ensure nodes exist
        self.add_user(referrer)
        self.add_user(candidate)

        # unique referrer constraint
        if candidate in self._parent:
            if self._parent[candidate] == referrer:
                return False  # duplicate edge; idempotent
            raise ValueError("unique referrer violation")

        # acyclicity: adding referrer -> candidate is illegal iff referrer is reachable from candidate
        if self._reachable(candidate, referrer):
            raise ValueError("adding this edge would create a cycle")

        # commit
        self._children[referrer].add(candidate)
        self._parent[candidate] = referrer
        return True

    def get_direct_referrals(self, user: str) -> List[str]:
        """Immediate children (direct referrals)."""
        if user not in self._nodes:
            return []
        return sorted(self._children[user])

    # ---- helpers ----
    def _reachable(self, src: str, dst: str) -> bool:
        """BFS from src to check if dst is reachable."""
        if src == dst:
            return True
        q = deque([src])
        seen = {src}
        while q:
            u = q.popleft()
            for v in self._children[u]:
                if v == dst:
                    return True
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return False

    # optional utilities
    def users(self) -> List[str]:
        return sorted(self._nodes)

    def parent_of(self, user: str) -> str | None:
        return self._parent.get(user)


    def reach_count(self, user: str) -> int:
            """
            Total downstream referrals (direct + indirect).
            Returns 0 for unknown users.
            BFS; counts unique descendants once.
            """
            if user not in self._nodes:
                return 0
            seen = set()
            q = deque(self._children[user])
            count = 0
            while q:
                v = q.popleft()
                if v in seen:
                    continue
                seen.add(v)
                count += 1
                for w in self._children[v]:
                    if w not in seen:
                        q.append(w)
            return count

    def top_k_referrers_by_reach(self, k: int) -> list[tuple[str, int]]:
        """
        Ranked list of (user, reach_count) for top k.
        Tie-break: alphabetical user id for determinism.
        k<=0 -> [] ; k>n -> all users.
        Note on choosing k: pick k to match your budget/ops capacity or review bandwidth.
        """
        if k <= 0:
            return []
        pairs = [(u, self.reach_count(u)) for u in self._nodes]
        pairs.sort(key=lambda x: (-x[1], x[0]))
        return pairs[:k]
    

    # ---- Part 3: influencer metrics (READ-ONLY) ----
    # Assumes Part 1 (DAG with unique parent per node) and Part 2 exist.
    # All methods below DO NOT mutate graph state.

    def reach_set(self, user: str) -> set[str]:
        """[Part 3] All unique descendants (direct + indirect)."""
        if user not in self._nodes:
            return set()
        seen = set()
        q = deque(self._children[user])
        while q:
            v = q.popleft()
            if v in seen:
                continue
            seen.add(v)
            q.extend(self._children[v])
        return seen

    def unique_reach_expansion(self, k: int) -> list[tuple[str, int]]:
        """
        [Part 3] Greedy maximum coverage:
        Iteratively pick user adding the largest number of NOT-YET-COVERED descendants.
        Returns ordered [(user, marginal_gain), ...]. Read-only.
        """
        if k <= 0 or not self._nodes:
            return []
        reach_map = {u: self.reach_set(u) for u in self._nodes}
        covered: set[str] = set()
        remaining = set(self._nodes)
        picked: list[tuple[str, int]] = []

        while remaining and len(picked) < k:
            best_user, best_gain = None, -1
            for u in remaining:
                gain = len(reach_map[u] - covered)
                if gain > best_gain or (gain == best_gain and (best_user is None or u < best_user)):
                    best_user, best_gain = u, gain
            if best_gain <= 0:
                break
            picked.append((best_user, best_gain))
            covered |= reach_map[best_user]
            remaining.remove(best_user)
        return picked

    # Flow centrality NOTE:
    # Part 1 enforces "unique referrer" => graph is a forest (each node has at most one parent).
    # In a forest, every s->t path is UNIQUE if it exists.
    # Therefore, node v lies on the (only) shortest path s->t  iff  s is an ancestor of v AND t is a descendant of v.
    # That gives a closed form:
    #   flow_centrality(v) = (#ancestors of v) * (#descendants of v)

    def _desc_counts(self) -> dict[str, int]:
        """[Part 3] Number of descendants for each node. Read-only DFS from roots."""
        counts: dict[str, int] = {}

        def dfs(u: str) -> int:
            total = 0
            for c in self._children[u]:
                total += 1 + dfs(c)
            counts[u] = total
            return total

        roots = [u for u in self._nodes if u not in self._parent]
        for r in roots:
            dfs(r)
        # ensure isolated nodes appear with 0
        for u in self._nodes:
            counts.setdefault(u, 0)
        return counts

    def _anc_counts(self) -> dict[str, int]:
        """[Part 3] Number of ancestors (distance to root) for each node. Read-only."""
        counts: dict[str, int] = {}

        def up(u: str) -> int:
            if u in counts:
                return counts[u]
            p = self._parent.get(u)
            counts[u] = 0 if p is None else up(p) + 1
            return counts[u]

        for u in self._nodes:
            up(u)
        return counts

    def flow_centrality(self) -> list[tuple[str, int]]:
        """
        [Part 3] Flow centrality in a forest:
        score(v) = ancestors(v) * descendants(v).
        Returns ranked list [(user, score)] desc; ties broken by user id.
        Read-only.
        """
        anc = self._anc_counts()
        desc = self._desc_counts()
        pairs = [(u, anc[u] * desc[u]) for u in self._nodes]
        pairs.sort(key=lambda x: (-x[1], x[0]))
        return pairs
