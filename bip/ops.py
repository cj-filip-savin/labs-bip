#
# Copyright (c) 2023 CUJO LLC
#
"""
This module contains business logic exposed via CLI and Web service.
"""
import logging

from bip.exceptions import ModError
from bip.mods import run_mods

logger = logging.getLogger("bip.ops")


def op_check(items: list[str]):
    """Performs analysis of `items` (URLs, hashes and local files)"""

    sample_data_list = [{"source": x, "ignore_keys": {"ignore_keys", "blob"}} for x in items]
    for sample_data in sample_data_list:
        logger.info("Checking %s", sample_data["source"])
        for mod in run_mods:
            try:
                mod(sample_data)
            except ModError as exc:
                sample_data["error"] = f"{mod.__name__}:{exc}"
                logging.getLogger(mod.__module__).error(exc)
                break  # Process next sample

    return sample_data_list
