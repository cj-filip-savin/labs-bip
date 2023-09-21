#
# Copyright (c) 2023 CUJO LLC
#
"""
This loader mod ensures file and blob is available for further processing.
If sample was already processed, previous results are loaded from DB.
"""
import hashlib
import json
import logging
import os
import re
from urllib.parse import urlparse
from zipfile import ZipFile

import requests

from bip import db
from bip.exceptions import ModError
from bip.mods.saver import SAMPLE_DIR, ZIP_PASSWORD
from bip.utils import make_temp_dir

# Disable if running as a web service
ALLOW_LOCAL_FILES = True

logger = logging.getLogger(__name__)


def loader(sample_data):
    """
    Main loader mod function.

    Reads `sample_data` keys:
    * `source`    - file path, URL or hash of the sample
    Writes `sample_data` keys:
    * `blob`      - sample content bytes
    * `hash`      - short hash of `blob` (first 8 chars of SHA256)
    * `file_name` - original name of local file or URL
    * `file_path` - full path to file containing sample (temp file used for URL)
    Raises `ModError`:
    * When URL source is not accessible
    * When local file source is not readable
    * When local file source is not allowed by `ALLOW_LOCAL_FILES`
    """
    _load_source(sample_data)
    _load_db(sample_data)


def _load_source(sample_data: dict):
    """Loads sample blob from source (e.g. file or URL)."""
    if re.match("^https://", sample_data["source"]):
        # Download file from URL to temp folder
        logger.debug("Fetching URL %s", sample_data["source"])
        url = sample_data["source"]
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ModError(f"HTTPError{exc.response.status_code}") from exc
        except requests.exceptions.RequestException as exc:
            raise ModError(exc.__class__.__name__) from exc
        sample_data["blob"] = resp.content
        sample_data["hash"] = hashlib.sha256(sample_data["blob"]).hexdigest()[:8]
        name = os.path.basename(urlparse(url).path)
        sample_data["file_name"] = name or f"UNKNOWN_{sample_data['hash']}"
        # Store downloaded sample in temp dir
        temp_dir = make_temp_dir()
        file_path = os.path.join(temp_dir, sample_data["file_name"])
        sample_data["file_path"] = file_path
        logger.debug("Saved to temp %s", file_path)
    elif re.match(r"^[0-9a-f]{8}$", sample_data["source"]):
        # Load file from existing sample ZIP
        logger.debug("Loading existing sample with hash %s", sample_data["source"])
        zip_file = os.path.join(SAMPLE_DIR, sample_data["source"] + ".zip")
        try:
            with ZipFile(zip_file) as zipf:
                with zipf.open('sample', pwd=ZIP_PASSWORD.encode('ascii')) as fp:
                    sample_data["blob"] = fp.read()
        except OSError as exc:
            raise ModError(exc.__class__.__name__) from exc
        temp_dir = make_temp_dir()
        sample_data["file_path"] = os.path.join(temp_dir, "sample")
        with open(sample_data["file_path"], "wb") as fp:
            fp.write(sample_data["blob"])
        sample_data["hash"] = sample_data["source"]
    else:
        # Load local file
        if not ALLOW_LOCAL_FILES:
            raise ModError("LocalFileNotAllowed")
        logger.debug("Loading local file %s", sample_data["source"])
        file = sample_data["source"]
        try:
            with open(file, "rb") as fp:
                sample_data["blob"] = fp.read()
        except OSError as exc:
            raise ModError(exc.__class__.__name__) from exc
        sample_data["hash"] = hashlib.sha256(sample_data["blob"]).hexdigest()[:8]
        sample_data["file_name"] = os.path.basename(file)
        sample_data["file_path"] = os.path.realpath(file)
    logger.info("Sample size is %d bytes", len(sample_data["blob"]))
    sample_data["ignore_keys"].add("blob")


def _load_db(sample_data: dict):
    """Loads previously processed sample data from DB."""
    sql = "SELECT data FROM sample WHERE hash = ?"
    row = db.execute(sql, (sample_data["hash"],)).fetchone()
    if not row:
        return

    db_sample_data = json.loads(row[0])
    logger.debug("Merged existing DB sample data for %s", sample_data["hash"])
    orig_sample_data = sample_data.copy()
    # Overwrite db_sample_data with orig_sample_data key/values
    sample_data.clear()
    sample_data.update({**db_sample_data, **orig_sample_data})
