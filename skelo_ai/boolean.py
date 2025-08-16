from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict, deque
import re

def backtrack_circuit_to_boolean_expressions(circuit: Dict[str, Any]) -> List[str]:
    """
    Mutate circuit['gates'][*]['connections'] FIRST:
      - Replace 'toggle' with concrete input labels A, B, C, ...
      - Replace 'probe'  with concrete output labels Y0, Y1, ...
      - Do it index-coupled: connections[i] uses connected_wires[i]
      - Wire IDs are bound to a single label and reused consistently.

    Then, backtrack from each probe (Yk) to inputs to produce "Yk = <expr>".

    Operators: ~ (NOT), & (AND), | (OR), ^ (XOR)
    NAND/NOR/XNOR are represented as ~( ... ) around the base op.
    """
    gates: List[Dict[str, Any]] = circuit.get("gates", [])
    toggles = circuit.get("toggles", [])
    probes  = circuit.get("probes", [])
    wires: Dict[str, List[List[int]]] = circuit.get("wires", {})

    # ---------------- 1) Labels ----------------
    in_labels  = [_alpha_label(i) for i in range(len(toggles))]   # A, B, C, ...
    out_labels = [f"Y{i}" for i in range(len(probes))]            # Y0, Y1, ...
    in_label_set = set(in_labels)

    # ---------------- 2) Geometry: wire ↔ toggle/probe ----------------
    wire_points: Dict[str, Set[Tuple[int,int]]] = {wid: {tuple(p) for p in pts} for wid, pts in wires.items()}
    toggle_ends = [(tuple(seg[0]), tuple(seg[1])) for seg in toggles]
    probe_ends  = [(tuple(seg[0]), tuple(seg[1])) for seg in probes]

    def hits(wid: str, ends: Tuple[Tuple[int,int], Tuple[int,int]]) -> bool:
        pts = wire_points.get(wid, set())
        a, b = ends
        return a in pts and b in pts

    wire_to_toggle_idx: Dict[str, int] = {}
    wire_to_probe_idx:  Dict[str, int] = {}
    for wid in wires.keys():
        for i, ends in enumerate(toggle_ends):
            if hits(wid, ends):
                wire_to_toggle_idx[wid] = i
                break
    for wid in wires.keys():
        for i, ends in enumerate(probe_ends):
            if hits(wid, ends):
                wire_to_probe_idx[wid] = i
                break

    # Persistent wire → label bindings (never change once set)
    wire_to_input_label  = {wid: in_labels[i]  for wid, i in wire_to_toggle_idx.items()}
    wire_to_output_label = {wid: out_labels[i] for wid, i in wire_to_probe_idx.items()}

    # ---------------- 3) MUTATE connections FIRST (index-coupled) ----------------
    # For connections[i], look at connected_wires[i] to choose the bound label.
    for g in gates:
        cw = g.get("connected_wires", [])
        conns = g.get("connections", [])
        new_conns = []
        for i, entry in enumerate(conns):
            if not (isinstance(entry, list) and len(entry) == 3):
                new_conns.append(entry)
                continue
            a, role, target = entry
            wid = cw[i] if i < len(cw) else None

            if target == "toggle":
                if wid and wid in wire_to_input_label:
                    new_conns.append([a, role, wire_to_input_label[wid]])
                else:
                    # fallback: deterministic but unbound
                    new_conns.append([a, role, in_labels[0] if in_labels else "A"])
            elif target == "probe":
                if wid and wid in wire_to_output_label:
                    new_conns.append([a, role, wire_to_output_label[wid]])
                else:
                    new_conns.append([a, role, out_labels[0] if out_labels else "Y0"])
            else:
                new_conns.append(entry)
        g["connections"] = new_conns

    # ---------------- 4) Backtracking helpers ----------------
    gates_by_id = {g["id"]: g for g in gates}

    # gate <- gate fan-in (use both directions so we’re robust to role mistakes)
    gate_inputs_from_gates: Dict[int, List[int]] = defaultdict(list)
    for g in gates:
        gid = g["id"]
        for a, role, tgt in g.get("connections", []):
            if role == "input" and isinstance(tgt, int) and tgt in gates_by_id:
                _push_unique(gate_inputs_from_gates[gid], tgt)
            elif role == "output" and isinstance(tgt, int) and tgt in gates_by_id:
                _push_unique(gate_inputs_from_gates[tgt], gid)

    # For geometry fallback of literals: collect, per gate, the input labels present on its wires
    gate_input_wire_labels: Dict[int, List[str]] = defaultdict(list)
    for g in gates:
        gid = g["id"]
        for wid in g.get("connected_wires", []):
            if wid in wire_to_input_label:
                lbl = wire_to_input_label[wid]
                if lbl not in gate_input_wire_labels[gid]:
                    gate_input_wire_labels[gid].append(lbl)

    # wire -> gates touching it (to find driver for each Yk)
    wire_to_gates: Dict[str, Set[int]] = defaultdict(set)
    for g in gates:
        for wid in g.get("connected_wires", []):
            wire_to_gates[wid].add(g["id"])

    # Determine driver gate for each probe using wires that carry that Yk
    probe_driver: Dict[int, int] = {}
    for pi, ylbl in enumerate(out_labels):
        candidates: Set[int] = set()
        for wid, lbl in wire_to_output_label.items():
            if lbl == ylbl:
                candidates |= wire_to_gates.get(wid, set())
        if candidates:
            probe_driver[pi] = min(candidates)  # deterministic

    # ---------------- 5) Backtrack expressions (now using concrete labels only) ----------------
    expr_cache: Dict[int, str] = {}
    visiting: Set[int] = set()

    def expr_for_gate(gid: int) -> str:
        if gid in expr_cache:
            return expr_cache[gid]
        if gid in visiting:
            return "<?>"
        visiting.add(gid)

        g = gates_by_id[gid]
        gtype = g["type"].upper()
        declared_n = g.get("num_inputs", None)

        # 1) Collect operands from mutated connections in order
        ops: List[str] = []
        used_in_labels: Set[str] = set()
        used_src_gates: Set[int] = set()

        for a, role, tgt in g.get("connections", []):
            if role != "input":
                continue
            if isinstance(tgt, int) and tgt in gates_by_id:
                used_src_gates.add(tgt)
                ops.append(expr_for_gate(tgt))
            elif isinstance(tgt, str):
                # Accept only input labels (A,B,...) as literals; ignore Y* as "input"
                if tgt in in_label_set:
                    used_in_labels.add(tgt)
                    ops.append(tgt)

        # 2) Add any missing gate inputs inferred from opposite-direction links
        for src in gate_inputs_from_gates.get(gid, []):
            if src not in used_src_gates:
                ops.append(expr_for_gate(src))

        # 3) Geometry fallback for literal inputs that weren’t captured as 'input' rows
        for lbl in gate_input_wire_labels.get(gid, []):
            if declared_n is not None and len(ops) >= declared_n:
                break
            if lbl not in used_in_labels:
                used_in_labels.add(lbl)
                ops.append(lbl)

        # 4) Enforce declared arity
        if declared_n is not None:
            ops = ops[:declared_n]

        out = _combine(gtype, ops)
        visiting.remove(gid)
        expr_cache[gid] = out
        return out

    results: List[str] = []
    for pi, ylbl in enumerate(out_labels):
        if pi not in probe_driver:
            results.append(f"{ylbl} = <unconnected>")
        else:
            rhs = expr_for_gate(probe_driver[pi])
            results.append(f"{ylbl} = {rhs}")
    return results


# ---------------- helpers ----------------

_IS_VAR = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

def _alpha_label(i: int) -> str:
    """A..Z, then A1..Z1, A2..Z2, ..."""
    if i < 26:
        return chr(ord('A') + i)
    return f"{chr(ord('A') + (i % 26))}{i // 26}"

def _push_unique(xs: List[int], v: int) -> None:
    if v not in xs:
        xs.append(v)

def _combine(gtype: str, ops: List[str]) -> str:
    """Combine with safe parentheses."""
    def P(s: str) -> str:
        return s if _IS_VAR.fullmatch(s or "") else f"({s})"
    if gtype == "NOT":
        return f"~{P(ops[0] if ops else '?')}"
    if gtype == "AND":
        return f"({' & '.join(P(x) for x in ops)})" if ops else "()"
    if gtype == "OR":
        return f"({' | '.join(P(x) for x in ops)})" if ops else "()"
    if gtype == "XOR":
        return f"({' ^ '.join(P(x) for x in ops)})" if ops else "()"
    if gtype == "NAND":
        return f"~({' & '.join(P(x) for x in ops)})" if ops else "~()"
    if gtype == "NOR":
        return f"~({' | '.join(P(x) for x in ops)})" if ops else "~()"
    if gtype == "XNOR":
        return f"~({' ^ '.join(P(x) for x in ops)})" if ops else "~()"
    # Fallback: AND
    return f"({' & '.join(P(x) for x in ops)})" if ops else "()"
