#
# Copyright (c) 2023 CUJO LLC
#
"""
This lisa mod sends sample to LiSa sandbox and retrieves report when it is available.
"""
import io
import logging

import requests

from bip.exceptions import ModError

LISA_URL = "http://localhost:4242"

logger = logging.getLogger(__name__)


def lisa(sample_data):
    """
    Main lisa mod function.

    Reads `sample_data` keys:
    * `blob`        - sample content bytes
    * `file_name`   - original name of local file or URL
    Writes `sample_data` keys:
    * `lisa_id`     - LiSa task id
    * `lisa_report` - LiSa report (when available)
    Raises `ModError`:
    * When communication with LiSa failed
    """
    try:
        if "lisa_id" not in sample_data:
            logger.debug("Sending sample to LiSa")
            fp = io.BytesIO(sample_data["blob"])
            fp.name = sample_data["file_name"]
            resp = requests.post(LISA_URL + "/api/tasks/create/file", files={"file": fp})
            resp.raise_for_status()
            sample_data["lisa_id"] = resp.json()["task_id"]
        else:
            logger.debug("Sample was already sent to LiSa, trying to get report")
            resp = requests.get(LISA_URL + "/api/report/" + sample_data["lisa_id"])
            if resp.status_code == 200:
                # Report
                sample_data["lisa_report"] = resp.json()
                sample_data["ignore_keys"].add("lisa_report")
                # VM log
                # resp = requests.get(LISA_URL + "/api/machinelog/" + sample_data["lisa_id"])
                # sample_data["lisa_vm_log"] = resp.text
                # sample_data["ignore_keys"].add("lisa_vm_log")
                # Program output
                # resp = requests.get(LISA_URL + "/api/output/" + sample_data["lisa_id"])
                # sample_data["lisa_program_output"] = resp.text
                # sample_data["ignore_keys"].add("lisa_program_output")
    except requests.exceptions.RequestException as exc:
        raise ModError(exc.__class__.__name__) from exc
