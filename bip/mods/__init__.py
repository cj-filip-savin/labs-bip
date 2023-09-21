#
# Copyright (c) 2023 CUJO LLC
#
"""
Subpackage containing BIP mods.
"""
from .loader import loader
from .hashes import hashes
from .history import history
from .saver import saver
from .lisa import lisa

# Enabled mods. Each sample executed through every mod.
# If mod raises `bip.exceptions.ModError` then execution stops and next sample is processed.
run_mods = [
    loader,
    history,
    hashes,
    lisa,
    saver
]
