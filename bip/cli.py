#
# Copyright (c) 2023 CUJO LLC
#
"""
This module contains BIP CLI frontend that exposes functions of `bip.ops`.
"""
from pprint import pp

from docopt import docopt

from bip import __program__, __version__, ops


def app():
    """CLI application."""
    help_str = f"""

>>> {__program__} v{__version__} <<<

BIP CLI - sample analysis

Usage:
    sengine check <what>...
    sengine --help
    sengine --version

Arguments:
    <what> local file, sample hash or URL pointing to file (will be downloaded) to check,
           or @file containing list of local files, hashes and URLs to check.

Examples: 
    sengine check ./z.arm64 http://12.23.34.56/x.mips @file.txt 84de9c61
    * will perform check of local file `z.arm64`
    * will download and perform check of `x.mips`
    * will perform check on all hashes, URLs and files listed in `file.txt`
    * will perform re-check of previously processed sample with hash `84de9c61`
"""
    arguments = docopt(help_str, help=True, version=__version__)

    items = []
    for item in arguments["<what>"]:
        if item[0] == "@":
            with open(item[1:], encoding="utf8") as fp:
                items += [l.strip() for l in fp.readlines()]
        else:
            items.append(item)

    if arguments["check"]:
        for result in ops.op_check(items):
            for key in ("blob", "ignore_keys"):
                if key in result:
                    del result[key]
            pp(result)
