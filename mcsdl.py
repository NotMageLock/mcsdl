import os
import requests

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

_manifest_cache = None


def _manifest():
    global _manifest_cache
    if _manifest_cache is None:
        r = requests.get(MANIFEST_URL)
        r.raise_for_status()
        _manifest_cache = r.json()
    return _manifest_cache


def versions():
    return [v["id"] for v in _manifest()["versions"]]


def releases():
    return [v["id"] for v in _manifest()["versions"] if v["type"] == "release"]


def snapshots():
    return [v["id"] for v in _manifest()["versions"] if v["type"] == "snapshot"]


def old_beta():
    return [v["id"] for v in _manifest()["versions"] if v["type"] == "old_beta"]


def old_alpha():
    return [v["id"] for v in _manifest()["versions"] if v["type"] == "old_alpha"]


def latest():
    return _manifest()["latest"]["release"]


def latest_snapshot():
    return _manifest()["latest"]["snapshot"]


def _version_meta(version):
    for v in _manifest()["versions"]:
        if v["id"] == version:
            r = requests.get(v["url"])
            r.raise_for_status()
            return r.json()
    raise ValueError(f"couldnt find version '{version}'")


def geturl(version: str):
    data = _version_meta(version)

    server = data.get("downloads", {}).get("server")
    if not server:
        raise ValueError(f"no server jar for '{version}'")

    return server["url"]

def download(version: str, path="server.jar", progress=None):
    url = geturl(version)

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        downloaded = 0

        with open(path, "wb") as f:
            for chunk in r.iter_content(65536):
                if not chunk:
                    continue

                f.write(chunk)
                downloaded += len(chunk)

                if progress:
                    progress(downloaded, total)

    return path
