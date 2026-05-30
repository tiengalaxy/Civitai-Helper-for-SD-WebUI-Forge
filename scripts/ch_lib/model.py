# -*- coding: UTF-8 -*-
import os
import json
from . import util
from . import civitai
from modules import shared


root_path = os.getcwd()
util.printD(f"Root Path is: {root_path}")

if root_path.startswith("~/"):
    user_home = os.path.expanduser("~")
    util.printD(f"Root Path is under User Home: {user_home}")
    root_path = os.path.join(user_home, root_path[2:])
    util.printD(f"Expanded Root Path is: {root_path}")


folders = {
    "ti": os.path.join(root_path, "embeddings"),
    "hyper": os.path.join(root_path, "models", "hypernetworks"),
    "ckp": os.path.join(root_path, "models", "Stable-diffusion"),
    "lora": os.path.join(root_path, "models", "Lora"),
    "controlnet": os.path.join(root_path, "models", "Controlnet"),
    "vae": os.path.join(root_path, "models", "VAE"),
    "upscaler": os.path.join(root_path, "models", "ESRGAN"),
}

exts = (".bin", ".pt", ".safetensors", ".ckpt", ".pth")
info_ext = ".info"
vae_suffix = ".vae"

model_type_display = {
    "ti": "Textual Inversion",
    "hyper": "Hypernetwork",
    "ckp": "Checkpoint",
    "lora": "LoRA",
    "controlnet": "ControlNet",
    "vae": "VAE",
    "upscaler": "Upscaler",
}


def get_custom_model_folder():
    util.printD("Get Custom Model Folder")

    global folders

    cmd_opts_map = {
        "ti": ("embeddings_dir",),
        "hyper": ("hypernetwork_dir",),
        "ckp": ("ckpt_dir",),
        "lora": ("lora_dir",),
        "controlnet": ("controlnet_dir",),
        "vae": ("vae_dir",),
        "upscaler": ("esrgan_dir", "upscale_models_dir"),
    }

    try:
        for model_type, opt_names in cmd_opts_map.items():
            for opt_name in opt_names:
                if hasattr(shared.cmd_opts, opt_name):
                    opt_val = getattr(shared.cmd_opts, opt_name, None)
                    if opt_val and os.path.isdir(opt_val):
                        folders[model_type] = opt_val
                        break
    except Exception as e:
        util.printD(f"Error loading custom model folders: {str(e)}")

    existing_folders = {}
    for key, path in folders.items():
        if os.path.isdir(path):
            existing_folders[key] = path
        else:
            util.printD(f"Model folder does not exist, skipping: {key} -> {path}")
    folders = existing_folders


def write_model_info(path, model_info):
    util.printD("Write model info to file: " + path)
    with open(os.path.realpath(path), 'w', encoding='utf-8') as f:
        json.dump(model_info, f, indent=4, ensure_ascii=False)


def load_model_info(path):
    try:
        with open(os.path.realpath(path), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        util.printD("Failed to load model info: " + path)
        util.printD(str(e))
        return None


def get_model_names_by_type(model_type:str) -> list:

    model_folder = folders[model_type]

    model_names = []
    for root, dirs, files in os.walk(model_folder, followlinks=True):
        for filename in files:
            item = os.path.join(root, filename)
            base, ext = os.path.splitext(item)
            if ext in exts:
                model_names.append(filename)

    return model_names


def get_model_path_by_type_and_name(model_type:str, model_name:str) -> str:
    util.printD("Run get_model_path_by_type_and_name")
    if model_type not in folders.keys():
        util.printD("unknown model_type: " + model_type)
        return

    if not model_name:
        util.printD("model name can not be empty")
        return

    folder = folders[model_type]

    for root, dirs, files in os.walk(folder, followlinks=True):
        for filename in files:
            if filename == model_name:
                model_root = root
                model_path = os.path.join(root, filename)
                return (model_root, model_path)

    return


def get_model_path_by_search_term(model_type:str, search_term:str):
    util.printD(f"Search model of {search_term} in {model_type}")
    if model_type not in folders.keys():
        util.printD("unknow model type: " + model_type)
        return

    has_hash = True
    if model_type == "hyper":
        has_hash = False
    elif search_term.endswith(exts):
        has_hash = False

    splited_path = search_term.split()
    model_sub_path = splited_path[0]
    if has_hash and len(splited_path) > 1:
        model_sub_path = " ".join(splited_path[:-1])

    model_sub_path = model_sub_path.replace("\\\\", "\\")
    if os.sep != "\\":
        model_sub_path = model_sub_path.replace("\\", os.sep)

    if model_sub_path[:1] == "/":
        model_sub_path = model_sub_path[1:]

    model_folder_name = civitai.model_folder_name_map.get(model_type, "Lora")

    if model_sub_path.startswith(model_folder_name):
        model_sub_path = model_sub_path[len(model_folder_name):]

        if model_sub_path.startswith("/") or model_sub_path.startswith("\\"):
            model_sub_path = model_sub_path[1:]

    if model_type == "hyper":
        if not model_sub_path.endswith(".pt"):
            model_sub_path = model_sub_path+".pt"

    model_folder = folders[model_type]

    model_path = os.path.join(model_folder, model_sub_path)

    util.printD("model_folder: " + model_folder)
    util.printD("model_sub_path: " + model_sub_path)
    util.printD("model_path: " + model_path)

    if not os.path.isfile(model_path):
        util.printD("Can not find model file: " + model_path)
        return

    return model_path


def has_info_and_preview(model_path:str) -> bool:
    if not model_path or not os.path.isfile(model_path):
        return False

    base, ext = os.path.splitext(model_path)
    info_file = base + ".civitai" + info_ext
    first_preview = base + ".png"
    sec_preview = base + ".preview.png"

    has_info = os.path.isfile(info_file)
    has_preview = os.path.isfile(first_preview) or os.path.isfile(sec_preview)

    return has_info and has_preview


def _has_preview(model_path:str) -> bool:
    if not model_path or not os.path.isfile(model_path):
        return False

    base, ext = os.path.splitext(model_path)
    first_preview = base + ".png"
    sec_preview = base + ".preview.png"

    return os.path.isfile(first_preview) or os.path.isfile(sec_preview)
