# -*- coding: UTF-8 -*-
import sys
import time
import requests
import os
from datetime import datetime
from . import util


dl_ext = ".downloading"

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


def _should_verify_ssl():
    """SSL verification is enabled by default. Only skip when a custom proxy
    is configured (e.g. local debugging proxy)."""
    return not bool(util.proxies)


def _request_with_retry(method, url, **kwargs):
    """HTTP request with exponential backoff retry."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = method(url, **kwargs)
            return resp
        except requests.exceptions.Timeout as e:
            last_error = e
            util.printD(f"Request timed out (attempt {attempt+1}/{MAX_RETRIES}): {url}")
        except Exception as e:
            last_error = e
            util.printD(f"Request failed (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}")
        if attempt < MAX_RETRIES - 1:
            wait = 2 ** attempt
            util.printD(f"Retrying in {wait}s...")
            time.sleep(wait)
    raise last_error


def dl(url, folder, filename, filepath):
    util.printD("Start downloading from: " + url)

    file_path = ""
    if filepath:
        file_path = filepath
    else:
        if not folder:
            util.printD("folder is none")
            return

        if not os.path.isdir(folder):
            util.printD("folder does not exist: "+folder)
            return

        if filename:
            file_path = os.path.join(folder, filename)

    verify_ssl = _should_verify_ssl()
    try:
        rh = _request_with_retry(
            requests.get, url,
            stream=True, verify=verify_ssl,
            headers=util.def_headers, proxies=util.proxies,
            timeout=REQUEST_TIMEOUT
        )
    except Exception as e:
        util.printD(f"Header request failed after {MAX_RETRIES} retries: {str(e)}")
        return

    total_size = int(rh.headers.get('Content-Length', -1))
    if total_size < 0:
        util.printD('This model requires an API key to download. More info: https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper#civitai-api-key')
        return
    util.printD(f"File size: {total_size}")

    if not file_path:
        filename = ""
        if "Content-Disposition" in rh.headers.keys():
            cd = rh.headers["Content-Disposition"].encode('latin1').decode('utf-8', errors='ignore')
            if "=" in cd:
                filename = cd.split("=", 1)[1].strip('"')
            if not filename:
                util.printD("Fail to get file name from Content-Disposition: " + cd)
                return

        if not filename:
            util.printD("Can not get file name from download url's header")
            return

        file_path = os.path.join(folder, filename)

    util.printD("Target file path: " + file_path)
    base, ext = os.path.splitext(file_path)

    # Use timestamp-based suffix for naming conflicts instead of unbounded counter
    if os.path.isfile(file_path):
        util.printD("Target file already exist, appending timestamp")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{base}_{ts}{ext}"
        base = os.path.splitext(file_path)[0]

    dl_file_path = base + dl_ext

    util.printD(f"Downloading to temp file: {dl_file_path}")

    downloaded_size = 0
    if os.path.exists(dl_file_path):
        downloaded_size = os.path.getsize(dl_file_path)

    util.printD(f"Downloaded size: {downloaded_size}")

    headers = {'Range': 'bytes=%d-' % downloaded_size}
    headers['User-Agent'] = util.def_headers['User-Agent']
    if util.civitai_api_key:
        headers["Authorization"] = f"Bearer {util.civitai_api_key}"

    try:
        r = _request_with_retry(
            requests.get, url,
            stream=True, verify=verify_ssl,
            headers=headers, proxies=util.proxies,
            timeout=REQUEST_TIMEOUT
        )
    except Exception as e:
        util.printD(f"Download request failed after {MAX_RETRIES} retries: {str(e)}")
        return

    try:
        with open(dl_file_path, "ab") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    downloaded_size += len(chunk)
                    f.write(chunk)
                    f.flush()

                    progress = int(50 * downloaded_size / total_size)
                    sys.stdout.reconfigure(encoding='utf-8')
                    sys.stdout.write("\r[%s%s] %d%%" % ('-' * progress, ' ' * (50 - progress), 100 * downloaded_size / total_size))
                    sys.stdout.flush()
    except Exception as e:
        util.printD(f"Download write failed: {str(e)}")
        return
    finally:
        print()

    downloaded_size = os.path.getsize(dl_file_path)
    if downloaded_size < total_size:
        util.printD(f"Download failed due to insufficient file size. Try again later or download it manually: {url}")
        return

    try:
        os.rename(dl_file_path, file_path)
    except OSError as e:
        util.printD(f"Failed to rename temp file: {str(e)}")
        return
    util.printD(f"File Downloaded to: {file_path}")
    return file_path
