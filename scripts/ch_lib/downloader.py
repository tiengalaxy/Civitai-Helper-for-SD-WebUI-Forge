# -*- coding: UTF-8 -*-
import sys
import requests
import os
from . import util


dl_ext = ".downloading"

requests.packages.urllib3.disable_warnings()

REQUEST_TIMEOUT = 30

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

    try:
        rh = requests.get(url, stream=True, verify=False, headers=util.def_headers, proxies=util.proxies, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        util.printD(f"Header request timed out after {REQUEST_TIMEOUT} seconds: {url}")
        return
    except Exception as e:
        util.printD(f"Header request failed: {str(e)}")
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
            filename = cd.split("=")[1].strip('"')
            if not filename:
                util.printD("Fail to get file name from Content-Disposition: " + cd)
                return

        if not filename:
            util.printD("Can not get file name from download url's header")
            return

        file_path = os.path.join(folder, filename)

    util.printD("Target file path: " + file_path)
    base, ext = os.path.splitext(file_path)

    count = 2
    new_base = base
    while os.path.isfile(file_path):
        util.printD("Target file already exist.")
        new_base = base + "_" + str(count)
        file_path = new_base + ext
        count += 1

    dl_file_path = new_base+dl_ext

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
        r = requests.get(url, stream=True, verify=False, headers=headers, proxies=util.proxies, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        util.printD(f"Download request timed out after {REQUEST_TIMEOUT} seconds: {url}")
        return
    except Exception as e:
        util.printD(f"Download request failed: {str(e)}")
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
