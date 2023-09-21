#
# Copyright (c) 2023 CUJO LLC
#
"""
This module contains BIP-specific errors and exceptions.
"""


class ModError(Exception):
    """
    These exceptions raised in `bip.mods.*` and causes immediate stop of sample processing,
    and start processing of next sample (if any).
    """


class ModFinishProcessing(Exception):
    """
    These exceptions raised in `bip.mods.*` and causes immediate stop of sample processing,
    saving result collected so far to the database,
    and start processing of next sample (if any).
    """
