# -*- coding: UTF-8 -*-
import os
import io
import hashlib
import requests
import shutil
import time
import logging

logger = logging.getLogger("CivitaiHelper")


version = "1.15.0"

def_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
               "Authorization": ""}


proxies = None
civitai_api_key = ""
civitai_domain = "civitai.red"


def printD(msg: str) -> None:
    """Print debug message to console (backward-compatible wrapper)."""
    print(f"Civitai Helper: {msg}")
    logger.debug(msg)


class RateLimiter:
    """Simple token-bucket rate limiter for API calls.

    Usage:
        limiter = RateLimiter(calls_per_second=1)
        limiter.wait()  # blocks if called too frequently
    """

    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / max(calls_per_second, 0.1)
        self.last_call = 0.0

    def wait(self) -> None:
        """Block until the next call is allowed."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

    def reset(self) -> None:
        """Reset the timer."""
        self.last_call = 0.0


# Global rate limiter instance (1 call/second by default)
api_rate_limiter = RateLimiter(calls_per_second=1.0)


def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk

def gen_file_sha256(filname: str) -> str:
    printD("Use Memory Optimized SHA256")
    blocksize=1 << 20
    h = hashlib.sha256()
    length = 0
    with open(os.path.realpath(filname), 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)

    hash_value =  h.hexdigest()
    printD("sha256: " + hash_value)
    printD("length: " + str(length))
    return hash_value



def download_file(url: str, path: str, timeout: int = 30) -> bool:
    printD("Downloading file from: " + url)
    try:
        r = requests.get(url, stream=True, headers=def_headers, proxies=proxies, timeout=timeout)
        if not r.ok:
            printD("Get error code: " + str(r.status_code))
            printD(r.text)
            return False

        with open(os.path.realpath(path), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        printD("File downloaded to: " + path)
        return True
    except requests.exceptions.Timeout:
        printD(f"Download timed out after {timeout} seconds: {url}")
        return False
    except Exception as e:
        printD(f"Download failed: {str(e)}")
        return False

def get_subfolders(folder: str) -> list:
    printD("Get subfolder for: " + folder)
    if not folder:
        printD("folder can not be None")
        return []

    if not os.path.isdir(folder):
        printD("path is not a folder")
        return []

    prefix_len = len(folder)
    subfolders = []
    for root, dirs, files in os.walk(folder, followlinks=True):
        for dir in dirs:
            full_dir_path = os.path.join(root, dir)
            subfolder = full_dir_path[prefix_len:]
            subfolders.append(subfolder)

    return subfolders


def get_relative_path(item_path: str, parent_path: str) -> str:
    if not item_path:
        return ""
    if not parent_path:
        return ""
    if not item_path.startswith(parent_path):
        return item_path

    relative = item_path[len(parent_path):]
    if relative[:1] == "/" or relative[:1] == "\\":
        relative = relative[1:]

    return relative