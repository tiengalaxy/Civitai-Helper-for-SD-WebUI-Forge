# -*- coding: UTF-8 -*-
import os
import time
import json
import re
import requests
from . import util
from . import model
from . import setting


suffix = ".civitai"

REQUEST_TIMEOUT = 30

model_type_dict = {
    "Checkpoint": "ckp",
    "TextualInversion": "ti",
    "Hypernetwork": "hyper",
    "LORA": "lora",
    "LoCon": "lora",
    "Controlnet": "controlnet",
    "VAE": "vae",
    "Upscaler": "upscaler",
    "Pose": "ti",
    "Workflows": "ckp",
    "AestheticGradient": "ti",
    "Wildcards": "ti",
    "Standard": "ckp",
}

model_folder_name_map = {
    "ti": "embeddings",
    "hyper": "hypernetworks",
    "ckp": "Stable-diffusion",
    "controlnet": "Controlnet",
    "vae": "VAE",
    "upscaler": "ESRGAN",
    "lora": "Lora",
}


def get_url_dict():
    domain = util.civitai_domain
    return {
        "modelPage": f"https://{domain}/models/",
        "modelId": f"https://{domain}/api/v1/models/",
        "modelVersionId": f"https://{domain}/api/v1/model-versions/",
        "hash": f"https://{domain}/api/v1/model-versions/by-hash/"
    }


def get_full_size_image_url(image_url, width):
    return re.sub(r'/width=\d+/', '/width=' + str(width) + '/', image_url)


def _api_get(url, not_found_label="model", timeout=REQUEST_TIMEOUT):
    util.printD("Request model info from civitai")

    try:
        r = requests.get(url, headers=util.def_headers, proxies=util.proxies, timeout=timeout)
        if not r.ok:
            if r.status_code == 404:
                util.printD(f"Civitai does not have this {not_found_label}")
                return {}
            else:
                util.printD("Get error code: " + str(r.status_code))
                util.printD(r.text)
                return

        try:
            content = r.json()
        except Exception as e:
            util.printD("Parse response json failed")
            util.printD(str(e))
            util.printD("response:")
            util.printD(r.text)
            return

        if not content:
            util.printD("error, content from civitai is None")
            return

        return content
    except requests.exceptions.Timeout:
        util.printD(f"API request timed out after {timeout} seconds")
        return
    except Exception as e:
        util.printD(f"API request failed: {str(e)}")
        return


def get_model_info_by_hash(hash:str, timeout=REQUEST_TIMEOUT):
    if not hash:
        util.printD("hash is empty")
        return

    url_dict = get_url_dict()
    return _api_get(url_dict["hash"]+hash, not_found_label="model", timeout=timeout)


def get_model_info_by_id(id:str, timeout=REQUEST_TIMEOUT) -> dict:
    if not id:
        util.printD("id is empty")
        return

    url_dict = get_url_dict()
    return _api_get(url_dict["modelId"]+str(id), not_found_label="model", timeout=timeout)


def get_version_info_by_version_id(id:str, timeout=REQUEST_TIMEOUT) -> dict:
    if not id:
        util.printD("id is empty")
        return

    url_dict = get_url_dict()
    return _api_get(url_dict["modelVersionId"]+str(id), not_found_label="model version", timeout=timeout)


def get_version_info_by_model_id(id:str) -> dict:

    model_info = get_model_info_by_id(id)
    if not model_info:
        util.printD(f"Failed to get model info by id: {id}")
        return

    if "modelVersions" not in model_info.keys():
        util.printD("There is no modelVersions in this model_info")
        return

    if not model_info["modelVersions"]:
        util.printD("modelVersions is None")
        return

    if len(model_info["modelVersions"])==0:
        util.printD("modelVersions is Empty")
        return

    def_version = model_info["modelVersions"][0]
    if not def_version:
        util.printD("default version is None")
        return

    if "id" not in def_version.keys():
        util.printD("default version has no id")
        return

    version_id = def_version["id"]

    if not version_id:
        util.printD("default version's id is None")
        return

    version_info = get_version_info_by_version_id(str(version_id))
    if not version_info:
        util.printD(f"Failed to get version info by version_id: {version_id}")
        return

    return version_info


def _normalize_search_term_path(path_part):
    path_part = path_part.replace("\\\\", "\\")
    if os.sep != "\\":
        path_part = path_part.replace("\\", os.sep)
    return path_part


def load_model_info_by_search_term(model_type, search_term):
    util.printD(f"Load model info of {search_term} in {model_type}")
    if model_type not in model.folders.keys():
        util.printD("unknow model type: " + model_type)
        return

    parts = search_term.split()
    path_part = parts[0] if parts else search_term
    path_part = _normalize_search_term_path(path_part)

    base, ext = os.path.splitext(path_part)
    model_info_base = base

    if model_info_base[:1] == "/":
        model_info_base = model_info_base[1:]

    model_folder = model.folders[model_type]
    model_folder_name = os.path.basename(model_folder)

    if model_info_base.startswith(model_folder_name):
        model_info_base = model_info_base[len(model_folder_name):]

        if model_info_base.startswith("/") or model_info_base.startswith("\\"):
            model_info_base = model_info_base[1:]

    model_info_filename = model_info_base + suffix + model.info_ext
    model_info_filepath = os.path.join(model_folder, model_info_filename)

    if not os.path.isfile(model_info_filepath):
        util.printD("Can not find model info file: " + model_info_filepath)
        return

    return model.load_model_info(model_info_filepath)


def load_model_info_by_model_path(model_path):
    util.printD(f"Load model info of {model_path}")

    base, ext = os.path.splitext(model_path)
    model_info_filepath = base + suffix + model.info_ext

    if not os.path.isfile(model_info_filepath):
        util.printD("Can not find model info file: " + model_info_filepath)
        return

    return model.load_model_info(model_info_filepath)


def get_model_names_by_type_and_filter(model_type:str, filter:dict) -> list:

    model_folder = model.folders[model_type]

    no_info_only = False
    empty_info_only = False

    if filter:
        if "no_info_only" in filter.keys():
            no_info_only = filter["no_info_only"]
        if "empty_info_only" in filter.keys():
            empty_info_only = filter["empty_info_only"]

    model_names = []
    for root, dirs, files in os.walk(model_folder, followlinks=True):
        for filename in files:
            item = os.path.join(root, filename)
            base, ext = os.path.splitext(item)
            if ext in model.exts:
                if no_info_only:
                    info_file = base + suffix + model.info_ext
                    if os.path.isfile(info_file):
                        continue

                if empty_info_only:
                    info_file = base + suffix + model.info_ext
                    if os.path.isfile(info_file):
                        model_info = model.load_model_info(info_file)
                        if model_info:
                            if "id" in model_info.keys():
                                continue

                model_names.append(filename)

    return model_names

def get_model_names_by_input(model_type, empty_info_only):
    return get_model_names_by_type_and_filter(model_type, {"empty_info_only":empty_info_only})


def get_model_id_from_url(url:str) -> str:
    util.printD("Run get_model_id_from_url")
    id = ""

    if not url:
        util.printD("url or model id can not be empty")
        return ""

    if url.isnumeric():
        id = str(url)
        return id

    s = re.sub("\\?.+$", "", url).split("/")
    if len(s) < 2:
        util.printD("url is not valid")
        return ""

    if s[-2].isnumeric():
        id  = s[-2]
    elif s[-1].isnumeric():
        id  = s[-1]
    else:
        util.printD("There is no model id in this url")
        return ""

    return id


def get_preview_image_by_model_path(model_path:str, max_size_preview, skip_nsfw_preview):
    if not model_path:
        util.printD("model_path is empty")
        return

    if not os.path.isfile(model_path):
        util.printD("model_path is not a file: "+model_path)
        return

    base, ext = os.path.splitext(model_path)
    sec_preview = base + ".preview.png"
    info_file = base + suffix + model.info_ext

    if not os.path.isfile(sec_preview):
        util.printD("Checking preview image for model: " + model_path)
        if os.path.isfile(info_file):
            model_info = model.load_model_info(info_file)
            if not model_info:
                util.printD("Model Info is empty")
                return

            if "images" in model_info.keys():
                if model_info["images"]:
                    for img_dict in model_info["images"]:
                        if "nsfw" in img_dict.keys():
                            if img_dict["nsfw"] and img_dict["nsfw"] != "None":
                                util.printD("This image is NSFW")
                                if skip_nsfw_preview:
                                    util.printD("Skip NSFW image")
                                    continue

                        preview_type = img_dict.get("type")
                        if preview_type != "image":
                            util.printD(f"Unsupported preview type: {preview_type}, ignore.")
                            continue

                        if "url" in img_dict.keys():
                            img_url = img_dict["url"]
                            if max_size_preview:
                                if "width" in img_dict.keys():
                                    if img_dict["width"]:
                                        img_url = get_full_size_image_url(img_url, img_dict["width"])

                            util.download_file(img_url, sec_preview)
                            break



def search_local_model_info_by_version_id(folder:str, version_id:int, walk:bool=False) -> dict:
    util.printD("Searching local model by version id")
    util.printD("folder: " + folder)
    util.printD("version_id: " + str(version_id))
    util.printD("walk: " + str(walk))

    if not folder:
        util.printD("folder is none")
        return

    if not os.path.isdir(folder):
        util.printD("folder is not a dir")
        return

    if not version_id:
        util.printD("version_id is none")
        return

    if walk:
        util.printD(f"Searching model version id {version_id} by walking in: {folder}")
        for root, dirs, files in os.walk(folder, followlinks=True):
            for filename in files:
                base, ext = os.path.splitext(filename)
                if ext == model.info_ext:
                    if len(base) < 9:
                        continue

                    if base[-8:] == suffix:
                        path = os.path.join(root, filename)
                        model_info = model.load_model_info(path)
                        if not model_info:
                            continue

                        if "id" not in model_info.keys():
                            continue

                        id = model_info["id"]
                        if not id:
                            continue

                        if str(id) == str(version_id):
                            util.printD(f"Found model: {path}")
                            return model_info

    else:
        util.printD(f"Searching model version id {version_id} under: {folder}")
        for filename in os.listdir(folder):
            base, ext = os.path.splitext(filename)
            if ext == model.info_ext:
                if len(base) < 9:
                    continue

                if base[-8:] == suffix:
                    path = os.path.join(folder, filename)
                    model_info = model.load_model_info(path)
                    if not model_info:
                        continue

                    if "id" not in model_info.keys():
                        continue

                    id = model_info["id"]
                    if not id:
                        continue

                    if str(id) == str(version_id):
                        return model_info

    return


def _safe_get(d, key, default=None):
    if not d:
        return default
    if key not in d:
        return default
    val = d.get(key, default)
    # Only treat None as missing; allow falsy values like 0, False, ""
    if val is None:
        return default
    return val


def check_model_new_version_by_path(model_path:str, delay:float=1) -> tuple:
    if not model_path:
        util.printD("model_path is empty")
        return

    if not os.path.isfile(model_path):
        util.printD("model_path is not a file: "+model_path)
        return

    base, ext = os.path.splitext(model_path)
    info_file = base + suffix + model.info_ext

    if not os.path.isfile(info_file):
        return

    model_info_file = model.load_model_info(info_file)
    if not model_info_file:
        return

    local_version_id = _safe_get(model_info_file, "id")
    if not local_version_id:
        return

    model_id = _safe_get(model_info_file, "modelId")
    if not model_id:
        return

    model_info = get_model_info_by_id(model_id)
    util.printD(f"delay:{delay} second")
    time.sleep(delay)

    if not model_info:
        return

    modelVersions = _safe_get(model_info, "modelVersions", [])
    if not modelVersions:
        return

    current_version = modelVersions[0]
    if not current_version:
        return

    current_version_id = _safe_get(current_version, "id")
    if not current_version_id:
        return

    util.printD(f"Compare version id, local: {local_version_id}, remote: {current_version_id} ")
    if current_version_id == local_version_id:
        return

    model_name = _safe_get(model_info, "name", "")
    new_version_name = _safe_get(current_version, "name", "")
    description = _safe_get(current_version, "description", "")
    downloadUrl = _safe_get(current_version, "downloadUrl", "")

    img_url = ""
    images = _safe_get(current_version, "images", [])
    if images and images[0]:
        img_url = _safe_get(images[0], "url", "")

    return (model_path, model_id, model_name, current_version_id, new_version_name, description, downloadUrl, img_url)


def check_models_new_version_by_model_types(model_types:list, delay:float=1, check_new_ver_exist_in_all_folder:bool=False) -> list:
    util.printD("Checking models' new version")

    if not model_types:
        return []

    mts = []
    if type(model_types) == str:
        mts.append(model_types)
    elif type(model_types) == list:
        mts = model_types
    else:
        util.printD("Unknow model types:")
        util.printD(model_types)
        return []

    new_versions = []

    for model_type, model_folder in model.folders.items():
        if model_type not in mts:
            continue

        util.printD("Scanning path: " + model_folder)
        for root, dirs, files in os.walk(model_folder, followlinks=True):
            for filename in files:
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model.exts:
                    r = check_model_new_version_by_path(item, delay)

                    if not r:
                        continue

                    model_path, model_id, model_name, current_version_id, new_version_name, description, downloadUrl, img_url = r
                    if not current_version_id:
                        continue

                    is_already_in_list = any(current_version_id == nv[3] for nv in new_versions)
                    if is_already_in_list:
                        util.printD("New version is already in list")
                        continue

                    if check_new_ver_exist_in_all_folder:
                        target_model_info = search_local_model_info_by_version_id(model_folder, current_version_id, check_new_ver_exist_in_all_folder)
                    else:
                        target_model_info = search_local_model_info_by_version_id(root, current_version_id, check_new_ver_exist_in_all_folder)
                    if target_model_info:
                        util.printD("New version is already existed")
                        continue

                    new_versions.append(r)

    return new_versions
