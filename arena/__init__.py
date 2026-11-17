"""Possession labelling for More than a Hack 2027 (team Arena).

Pipeline: tracking -> per-frame distances to the ball -> Viterbi decoding with switch penalties
-> frame,label CSV. Every printed output is an aggregate; no frame-level data is ever printed.
"""
