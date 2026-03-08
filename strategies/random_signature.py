# -*- coding: utf-8 -*-
"""
Random-signature strategy for the train carriage problem.

This is a readability-focused refactor of the current repository version.

The intended behaviour is unchanged:
- move forward while writing a deterministic pseudo-random bit signature,
- compare the most recent observations against the signature prefix,
- when a sufficiently long match is found, toggle once and walk back to verify,
- if verification succeeds, return the inferred ring length,
- otherwise resume forward search and continue extending the signature.

Notes on internal state:
- ``global_step`` is a monotone logical step index used by this strategy.
  It is *not* reduced modulo ``n`` because ``n`` is unknown until termination.
- ``written`` stores the intended signature bits in write order, regardless of
  whether the lamp had to be toggled to realize that bit.
- ``observed`` stores the lamp states seen while moving forward.
- ``history`` currently records the first seen lamp state for each logical step.
  The verification path ultimately compares against ``written``. ``history`` is
  retained for compatibility and future diagnostics.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

StrategyResult = Tuple[bool, int, dict, bool, Optional[int]]


def train_strategy_random_signature(
    lamp_state: int,
    memory: dict,
    a: float = 0.5,
    b: float = 0.5,
    min_l: int = 3,
    get_title: bool = False,
) -> StrategyResult | str:
    if get_title:
        return f"Random Signature a={a:.1f} b={b:.1f} n={min_l}"

    if not memory:
        _initialize_memory(memory, a=a, b=b, min_l=min_l)

    toggle = False
    done = False
    estimated_n = None
    move = memory.get("last_move", +1) or +1

    global_step = memory["global_step"]
    pos_key = _position_key(global_step)
    memory["history"].setdefault(pos_key, lamp_state)

    phase = memory["phase"]

    if phase == "write":
        desired = _append_next_signature_bit(memory)
        if lamp_state != desired:
            toggle = True
        memory["phase"] = "search"
        move = +1
        memory["last_move"] = move
        memory["global_step"] = global_step + 1
        return toggle, move, memory, done, estimated_n

    if phase == "search":
        observed: Deque[int] = memory["observed"]
        observed.append(lamp_state)

        k = memory["global_step"]
        min_required_match = _compute_required_match_length(memory, k)

        if len(observed) >= min_required_match and len(memory["written"]) >= min_required_match:
            matching_len = _matching_prefix_suffix_len(
                observed=list(observed),
                written=memory["written"],
            )
            memory["matching_len"] = matching_len

            if matching_len >= min_required_match:
                memory["found_match_at_step"] = k
                memory["k_when_found"] = k
                memory["l_when_found"] = min_required_match
                memory["back_target_step"] = matching_len - 1
                memory["phase"] = "back"
                memory["toggle_done"] = True

                toggle = True
                move = -1
                memory["last_move"] = move
                memory["global_step"] = global_step - 1
                return toggle, move, memory, done, estimated_n

        desired = _append_next_signature_bit(memory)
        if lamp_state != desired:
            toggle = True

        move = +1
        memory["last_move"] = move
        memory["global_step"] = global_step + 1
        return toggle, move, memory, done, estimated_n

    if phase == "back":
        current_step = memory["global_step"]
        pos = _position_key(current_step)

        if pos in memory["history"]:
            # The current repository logic ultimately verifies against the
            # signature bit written at the same logical index. We keep that
            # behaviour explicit here.
            if pos >= len(memory["written"]):
                return False, 0, memory, True, -1

            expected_bit = memory["written"][pos]
            if lamp_state != expected_bit:
                k = memory["k_when_found"]
                candidate_origin_step = current_step
                n_est = k - candidate_origin_step
                if n_est and n_est > 0:
                    done = True
                    estimated_n = n_est
                    memory["estimated_n"] = n_est
                    memory["phase"] = "done"
                    memory["last_move"] = 0
                    return toggle, 0, memory, done, estimated_n

        if current_step > memory["back_target_step"]:
            move = -1
            memory["last_move"] = move
            memory["global_step"] = current_step - 1
            return toggle, move, memory, done, estimated_n

        memory["resume_step"] = memory["k_when_found"] - 1
        memory["phase"] = "resume"
        move = +1
        memory["last_move"] = move
        memory["global_step"] = current_step + 1
        return toggle, move, memory, done, estimated_n

    if phase == "resume":
        current_step = memory["global_step"]
        target = memory["resume_step"]

        if current_step < target:
            move = +1
            memory["last_move"] = move
            memory["global_step"] = current_step + 1
            return toggle, move, memory, done, estimated_n

        memory["phase"] = "write"
        move = +1
        memory["last_move"] = move
        memory["global_step"] = current_step + 1
        return toggle, move, memory, done, estimated_n

    if phase == "done":
        done = True
        estimated_n = memory.get("estimated_n")
        memory["last_move"] = 0
        return False, 0, memory, done, estimated_n

    move = +1
    memory["last_move"] = move
    memory["global_step"] = global_step + 1
    return toggle, move, memory, done, estimated_n


def _initialize_memory(memory: Dict, a: float, b: float, min_l: int) -> None:
    memory["phase"] = "search"
    memory["global_step"] = 0
    memory["pattern_len"] = 0

    memory["prng_state"] = 123456789
    memory["lcg_mod"] = 2**31
    memory["lcg_mul"] = 1103515245
    memory["lcg_inc"] = 12345

    memory["a"] = a
    memory["b"] = b
    memory["min_l"] = min_l

    memory["max_l_cap"] = memory["pattern_len"]
    memory["written_len"] = 0
    memory["found_match_at_step"] = None
    memory["back_target_step"] = None
    memory["resume_step"] = None
    memory["last_move"] = +1
    memory["toggle_done"] = False

    memory["written"] = []
    memory["observed"] = deque()
    memory["history"] = {}
    memory["pattern"] = []


def _prng_next_bit(memory: Dict) -> int:
    state = memory["prng_state"]
    state = (memory["lcg_mul"] * state + memory["lcg_inc"]) % memory["lcg_mod"]
    memory["prng_state"] = state
    return (state >> 16) & 1


def _position_key(step: int) -> int:
    # Kept intentionally monotone: n is unknown before termination.
    return step


def _compute_required_match_length(memory: Dict, k: int) -> int:
    if k > 0:
        val = math.ceil(memory["a"] * (k ** memory["b"]))
    else:
        val = memory["min_l"]
    return int(max(memory["min_l"], val))


def _matching_prefix_suffix_len(observed: List[int], written: List[int]) -> int:
    """
    Return the helper result used by the current repository implementation.

    Important: this intentionally preserves the original semantics, including
    the unusual ``test_len = 0`` case where ``observed[-0:]`` means the full
    list in Python and therefore never contributes useful evidence. This keeps
    the refactor behaviour-neutral relative to the existing strategy.
    """
    best = 0
    for test_len in range(len(written) - 1):
        if observed[-test_len:] == written[:test_len]:
            best = test_len
    return best


def _append_next_signature_bit(memory: Dict) -> int:
    desired = _prng_next_bit(memory)
    memory["pattern"].append(desired)
    memory["written"].append(desired)
    memory["written_len"] += 1
    return desired


def train_strategy_random_signature_a090_b060_n8(
    lamp_state: int, memory: dict, get_title: bool = False
):
    return train_strategy_random_signature(
        lamp_state, memory, a=0.9, b=0.6, min_l=8, get_title=get_title
    )


def train_strategy_random_signature_a0025_b01_n12(
    lamp_state: int, memory: dict, get_title: bool = False
):
    return train_strategy_random_signature(
        lamp_state, memory, a=0.6, b=0.6, min_l=10, get_title=get_title
    )


def train_strategy_random_signature_a050_b090_n7(
    lamp_state: int, memory: dict, get_title: bool = False
):
    return train_strategy_random_signature(
        lamp_state, memory, a=0.5, b=0.9, min_l=7, get_title=get_title
    )


def train_strategy_random_signature_a050_b080_n7(
    lamp_state: int, memory: dict, get_title: bool = False
):
    return train_strategy_random_signature(
        lamp_state, memory, a=0.5, b=0.8, min_l=7, get_title=get_title
    )
