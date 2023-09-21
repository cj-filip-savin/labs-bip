#
# Copyright (c) 2023 CUJO LLC
#
"""
This saver mod provides persistence of sample and its check result.
"""
import json
import logging
import os.path
import shutil

import pyminizip

from bip import db
from bip.utils import remove_ignored_keys, make_temp_dir

COMPRESS_LEVEL = 9
SAMPLE_DIR = "data/samples"
ZIP_PASSWORD = "infected"

logger = logging.getLogger(__name__)


def saver(sample_data):
    """
    Main saver mod function.

    * Reads all``sample_data`keys, excludes `ignore_keys` and writes to DB
    * Writes sample file to password-protected ZIP file in `SAMPLE_DIR`

    Check result
    """
    # Write sample data to DB excluding `ignore_keys`
    sql = """
    INSERT INTO sample(hash, data) VALUES(?, ?) 
    ON CONFLICT(hash) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP
    """
    sample_json = json.dumps(remove_ignored_keys(sample_data))
    db.execute(sql, (sample_data["hash"], sample_json), commit=True)
    # Save to ZIP
    zip_file = os.path.join(SAMPLE_DIR, sample_data["hash"] + ".zip")
    if not os.path.exists(zip_file):
        logger.debug("Writing %s", zip_file)
        temp_dir = make_temp_dir()
        src = os.path.join(temp_dir, "sample")
        shutil.copy(sample_data["file_path"], src)
        pyminizip.compress(src, None, zip_file, ZIP_PASSWORD, int(COMPRESS_LEVEL))
