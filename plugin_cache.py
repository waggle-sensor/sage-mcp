import os
import json
import requests
from datetime import datetime, timedelta

PLUGIN_MASTER_URL = "https://auth.sagecontinuum.org/plugins/"  # Replace with actual endpoint if different
CACHE_FILE = "plugin_metadata_cache.json"
CACHE_EXPIRY_HOURS = 24

def _is_cache_valid():
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        timestamp = cache.get("_timestamp")
        if not timestamp:
            return False
        cache_time = datetime.fromisoformat(timestamp)
        if datetime.utcnow() - cache_time < timedelta(hours=CACHE_EXPIRY_HOURS):
            return True
        return False
    except Exception:
        return False

def _load_cache():
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
    return cache["data"]

def _save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump({"_timestamp": datetime.utcnow().isoformat(), "data": data}, f)

def get_plugin_metadata(force_refresh=False):
    """
    Fetch and cache plugin metadata from the master URL. Returns the cached data unless force_refresh is True or cache is expired.
    """
    if not force_refresh and _is_cache_valid():
        return _load_cache()
    # Fetch from master URL
    response = requests.get(PLUGIN_MASTER_URL)
    if response.status_code == 200:
        data = response.json()
        _save_cache(data)
        return data
    else:
        # If fetch fails and cache exists, return cache
        if os.path.exists(CACHE_FILE):
            return _load_cache()
        raise RuntimeError(f"Failed to fetch plugin metadata: {response.status_code}")

if __name__ == "__main__":
    # Example usage: print plugin metadata, force refresh if --force is passed
    import sys
    force = "--force" in sys.argv
    plugins = get_plugin_metadata(force_refresh=force)
    print(json.dumps(plugins, indent=2)) 