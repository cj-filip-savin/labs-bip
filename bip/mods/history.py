#
# Copyright (c) 2023 CUJO LLC
#
"""
This history mod tracks history of known sample sources and file names
"""
from bip import db
from bip.utils import is_sample_hash


def history(sample_data):
    """
    Main history mod function.

    Reads `sample_data` keys:
    * `hash`      - short hash of `blob` (first 8 chars of SHA256)
    * `source`    - file path, URL or hash of the sample
    * `file_name` - original name of local file or URL
    Writes `sample_data` keys:
    * `history`             - list of timestamp, file name and source of the sample
    * `known_file_names`    - all known file names of the sample
    * `known_sources`       - all known sources of the sample

    If source is a hash (sample reprocessing) then it is not written to history.
    """
    # Write file name and source to known tables (if not already there)
    if not is_sample_hash(sample_data["source"]):
        sql = "INSERT OR IGNORE INTO sample_history(hash, file_name, source) VALUES(?, ?, ?)"
        values = (sample_data["hash"], sample_data["file_name"], sample_data["source"])
        db.execute(sql, values, commit=True)
    # Load history from DB
    sql = "SELECT timestamp, file_name, source FROM sample_history WHERE hash = ?"
    sample_data["history"] = []
    for row in db.execute(sql, (sample_data["hash"],)).fetchall():
        sample_data["history"].append({
            "timestamp": row[0],
            "file_name": row[1],
            "source": row[2]
        })
    sample_data["known_file_names"] = [x["file_name"] for x in sample_data["history"]]
    sample_data["known_sources"] = [x["source"] for x in sample_data["history"]]
    sample_data["ignore_keys"].add("history")
