#
# Copyright (c) 2023 CUJO LLC
#
"""
This hashlib mod calculates various hashes for the sample
"""
import hashlib

def hashes(sample_data):
    """
    Main hashes mod function.

    Reads `sample_data` keys:
    * `blob`        - sample bytes
    Writes `sample_data` keys:
    * `hash_sha256` - SHA256 of sample
    * `hash_sha1`   - SHA1 of sample
    * `hash_md5`    - MD5 of sample
    """
    if not all(x in ("hash_sha256", "hash_sha1", "hash_md5") for x in sample_data.keys()):
        sample_data["hash_sha256"] = hashlib.sha256(sample_data["blob"]).hexdigest()
        sample_data["hash_sha1"] = hashlib.sha1(sample_data["blob"]).hexdigest()
        sample_data["hash_md5"] = hashlib.md5(sample_data["blob"]).hexdigest()
