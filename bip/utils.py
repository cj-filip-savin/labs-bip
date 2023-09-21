#
# Copyright (c) 2023 CUJO LLC
#
"""
This module contains BIP utility functions.
"""
import re
from tempfile import TemporaryDirectory


def is_sample_hash(s: str):
    """Returns if string `s` is 8-char hash used for sample identifying"""
    return bool(re.match(r"^[0-9a-f]{8}$", s))

def remove_ignored_keys(d: dict):
    """Returns new `dict` with keys specified in `ignore_keys` removed"""
    data = dict(d)
    ignore_keys = d["ignore_keys"]
    for key in d.keys():
        if key in ignore_keys:
            del data[key]
    return data

# Holder for created temp dirs
_temp_dirs = []

def make_temp_dir():
    """Creates temporary directory for sample storage (directory removed at program exit)"""
    temp_dir = TemporaryDirectory(prefix="bip_sample_")  # pylint: disable=consider-using-with
    _temp_dirs.append(temp_dir)
    return temp_dir.name
