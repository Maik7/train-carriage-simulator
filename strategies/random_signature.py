# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 12:59:54 2025

@author: mjustus mit copilot
"""


import math
from collections import deque

def train_strategy_random_signature(lamp_state: int, memory: dict, a = 0.5, b = 0.5, min_l = 3 ):
    """
    Angepasste Strategie:
    - l = max(min_l, ceil(a*k**b)) 
    - Bei bekanntem n werden Positionen modulo n verwaltet (history pro Wagenindex).
    - Bei unbekanntem n bleibt die monotone global_step-Indexierung erhalten.
    """
    # --- Initialisierung ---
    #print(memory)
    if memory == {}:
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
        memory["history"] = {} # key: position_key (see below) -> first-seen bit
        # Pre-generate pattern
        s = memory["prng_state"]
        pattern = []
        for _ in range(memory["pattern_len"]):
            s = (memory["lcg_mul"] * s + memory["lcg_inc"]) % memory["lcg_mod"]
            pattern.append((s >> 16) & 1)
        memory["prng_state"] = s
        memory["pattern"] = pattern

    # --- Hilfsfunktionen ---
    def prng_next_bit():
        s = memory["prng_state"]
        s = (memory["lcg_mul"] * s + memory["lcg_inc"]) % memory["lcg_mod"]
        memory["prng_state"] = s
        return (s >> 16) & 1

    def position_key(step):
        """
        Liefert den Schlüssel, unter dem wir history speichern:
        
        """
       
        return step

    def compute_l(k):
        """
        l = max(min_l, ceil(a*k**b)) 
        Anschließend cap auf [min_l, max_l_cap].
        """
        a = memory.get("a", 1.0)
        b = memory.get("b", 1.0)
        val = math.ceil(a * (k ** b)) if k > 0 else memory.get("min_l", 1)
        val = max(memory.get("min_l", 1), val)
        #val = min(val, memory.get("max_l_cap", memory.get("pattern_len", 20)))
        return int(val)

    def get_matching_len(observed,written):
        best_matching_len = 0
        for test_len  in range(len(written)-1):
            last_l_observed = list(observed)[-test_len:]
            first_l_written = memory["written"][:test_len]
            if last_l_observed == first_l_written:
                best_matching_len = test_len
        return best_matching_len    

    # --- Default-Ausgaben ---
    toggle = False
    done = False
    estimated_n = None
    move = memory.get("last_move", +1) or +1

    gs = memory["global_step"]
    pos_key = position_key(gs)

    # Record first-seen lamp_state for this position_key if not present
    if pos_key not in memory["history"]:
        memory["history"][pos_key] = lamp_state

    # Append to observed sliding window
    observed = memory["observed"]
    observed.append(lamp_state)
    #if len(observed) > memory["pattern_len"]:
    #    observed.popleft()

    phase = memory["phase"]

    # --- WRITE ---
    if phase == "write": #like search, but just write
        idx = memory["written_len"]
        
        desired = prng_next_bit()
        memory["pattern"].append(desired)
        # write desired bit by toggling if needed
        if lamp_state != desired:
            toggle = True
        memory["written"].append(desired)
        memory["written_len"] += 1
        # nach Schreiben in Suchphase wechseln
        memory["phase"] = "search"
        move = +1
        memory["last_move"] = move
        memory["global_step"] = gs + 1
        return toggle, move, memory, done, estimated_n

    # --- SEARCH ---
    if phase == "search":
        k = memory["global_step"] # "k" wie in deiner Beschreibung (Schrittindex)
        l = compute_l(k)
        # Warten bis wir mindestens l beobachtete und l geschriebene Bits haben
        if len(observed) >= l and len(memory["written"]) >= l:
            # Wir vergleichen die letzten l beobachteten Bits mit den ersten l geschriebenen Bits.
            matching_len = get_matching_len(list(observed),memory["written"])
            memory["matching_len"] = matching_len
            if matching_len >= l:
                memory["found_match_at_step"] = k
                memory["k_when_found"] = k
                memory["l_when_found"] = l
                toggle = True
                memory["toggle_done"] = True
                #memory["back_target_step"] = k - l - 1
                memory["back_target_step"] = l - 1
                memory["phase"] = "back"
                move = -1
                memory["last_move"] = move
                memory["global_step"] = gs - 1
                return toggle, move, memory, done, estimated_n
        # kein Match -> nun schreiben (Phase bleibt search)
        memory["phase"] = "search"
        move = +1
        memory["last_move"] = move
        memory["global_step"] = gs + 1
        desired = prng_next_bit()
        memory["pattern"].append(desired)
        if lamp_state != desired:
            toggle = True
        memory["written"].append(desired)
        memory["written_len"] += 1
        #print(toggle, move, memory, done, estimated_n)
        return toggle, move, memory, done, estimated_n

    # --- BACK (zur Verifikation) ---
    if phase == "back":
        current_step = memory["global_step"]
        pos = position_key(current_step)
        # Prüfe, ob der aktuelle Wagen sich gegenüber dem ersten Besuch geändert hat
        if pos in memory["history"]:
            before = memory["history"][pos]
            if pos>=len(memory["written"]):
                return False, 0, memory, True, -1
                
            before = memory["written"][pos]
            if lamp_state != before:
                # Änderung gefunden: berechne n
                k = memory["k_when_found"]
                m_step = current_step
                
                n_est = k - m_step
                # Falls negative oder 0 (Zählkonventionen), ignoriere und fahre fort
                if n_est <= 0:
                    n_est = None
                    
                if n_est and n_est > 0:
                    done = True
                    estimated_n = n_est
                    memory["phase"] = "done"
                    memory["last_move"] = 0
                    return toggle, 0, memory, done, estimated_n
        # noch nicht am back_target -> weiter rückwärts
        if current_step > memory["back_target_step"]:
            move = -1
            memory["last_move"] = move
            memory["global_step"] = current_step - 1
            return toggle, move, memory, done, estimated_n
        else:
            # Verifikation fehlgeschlagen -> vorwärts zum resume Punkt
            resume = memory["k_when_found"] - 1 
            memory["resume_step"] = resume
            memory["phase"] = "resume"
            move = +1
            memory["last_move"] = move
            memory["global_step"] = current_step + 1
            return toggle, move, memory, done, estimated_n

    # --- RESUME ---
    if phase == "resume":
        current_step = memory["global_step"]
        target = memory["resume_step"]
        if current_step < target:
            move = +1
            memory["last_move"] = move
            memory["global_step"] = current_step + 1
            return toggle, move, memory, done, estimated_n
        else:
            memory["phase"] = "write"
            move = +1
            memory["last_move"] = move
            memory["global_step"] = current_step + 1
            return toggle, move, memory, done, estimated_n

    # --- DONE ---
    if phase == "done":
        done = True
        estimated_n = memory.get("estimated_n", None)
        memory["last_move"] = 0
        return False, 0, memory, done, estimated_n

    # Fallback: weiter vorwärts
    move = +1
    memory["last_move"] = move
    memory["global_step"] = gs + 1
    return toggle, move, memory, done, estimated_n

def train_strategy_random_signature_a050_b100_n7(lamp_state: int, memory: dict, get_title = False):
    if get_title:
        return "Random Signature a0.5 b1 n7"
    else:
        return  train_strategy_random_signature(lamp_state, memory, a = 0.5, b = 1, min_l = 7 )

def train_strategy_random_signature_a050_b090_n7(lamp_state: int, memory: dict, get_title = False):
    if get_title:
        return "Random Signature a0.5 b0.9 n7"
    else:
        return  train_strategy_random_signature(lamp_state, memory, a = 0.5, b = .9, min_l = 7 )

def train_strategy_random_signature_a050_b080_n7(lamp_state: int, memory: dict, get_title = False):
    if get_title:
        return "Random Signature a0.5 b0.8 n7"
    else:
        return  train_strategy_random_signature(lamp_state, memory, a = 0.5, b = .8, min_l = 7 )



