import json
import urllib.request


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.load(resp)
