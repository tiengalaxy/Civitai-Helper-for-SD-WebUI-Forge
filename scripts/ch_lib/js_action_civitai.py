# -*- coding: UTF-8 -*-
import os
import json
import requests
import webbrowser
from . import util
from . import model
from . import civitai
from . import msg_handler
from . import downloader



def _load_model_info_from_msg(result):
    model_type = result.get("model_type", "")
    model_path = result.get("model_path", "")
    search_term = result.get("search_term", "")

    if model_path:
        return civitai.load_model_info_by_model_path(model_path), model_type, search_term, model_path
    else:
        return civitai.load_model_info_by_search_term(model_type, search_term), model_type, search_term, ""


def open_model_url(msg, open_url_with_js):
    util.printD("Start open_model_url")

    output = ""
    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return

    model_info, model_type, search_term, model_path = _load_model_info_from_msg(result)

    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return ""

    model_id = model_info.get("modelId")
    if not model_id:
        util.printD(f"Failed to get model id from info file for {model_type} {search_term}")
        return ""

    url = civitai.get_url_dict()["modelPage"]+str(model_id)

    content = {
        "url":""
    }

    if not open_url_with_js:
        util.printD("Open Url: " + url)
        webbrowser.open_new_tab(url)
    else:
        util.printD("Send Url to js")
        content["url"] = url
        output = msg_handler.build_py_msg("open_url", content)

    util.printD("End open_model_url")
    return output



def add_trigger_words(msg):
    util.printD("Start add_trigger_words")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return

    prompt = result.get("prompt", "")
    model_info, model_type, search_term, model_path = _load_model_info_from_msg(result)

    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, prompt]

    trainedWords = model_info.get("trainedWords", [])
    if not trainedWords:
        util.printD(f"No trainedWords from info file for {model_type} {search_term}")
        return [prompt, prompt]

    trigger_words = ", ".join(trainedWords)
    new_prompt = prompt + " " + trigger_words
    util.printD("trigger_words: " + trigger_words)
    util.printD("prompt: " + prompt)
    util.printD("new_prompt: " + new_prompt)

    util.printD("End add_trigger_words")

    return [new_prompt, new_prompt]



def use_preview_image_prompt(msg):
    util.printD("Start use_preview_image_prompt")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return

    prompt = result.get("prompt", "")
    neg_prompt = result.get("neg_prompt", "")
    model_info, model_type, search_term, model_path = _load_model_info_from_msg(result)

    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]

    images = model_info.get("images", [])
    if not images:
        util.printD(f"No images from info file for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]

    preview_prompt = ""
    preview_neg_prompt = ""
    for img in images:
        meta = img.get("meta")
        if meta:
            preview_prompt = meta.get("prompt", "") or ""
            preview_neg_prompt = meta.get("negativePrompt", "") or ""
            if preview_prompt:
                break

    if not preview_prompt:
        util.printD(f"There is no prompt of {model_type} {search_term} in its preview image")
        return [prompt, neg_prompt, prompt, neg_prompt]

    util.printD("End use_preview_image_prompt")

    return [preview_prompt, preview_neg_prompt, preview_prompt, preview_neg_prompt]


def dl_model_new_version(msg, max_size_preview, skip_nsfw_preview):
    util.printD("Start dl_model_new_version")

    output = ""

    result = msg_handler.parse_js_msg(msg)
    if not result:
        output = "Parsing js ms failed"
        util.printD(output)
        return output

    model_path = result.get("model_path", "")
    version_id = result.get("version_id", "")
    download_url = result.get("download_url", "")

    util.printD("model_path: " + model_path)
    util.printD("version_id: " + str(version_id))
    util.printD("download_url: " + download_url)

    if not model_path:
        output = "model_path is empty"
        util.printD(output)
        return output

    if not version_id:
        output = "version_id is empty"
        util.printD(output)
        return output

    if not download_url:
        output = "download_url is empty"
        util.printD(output)
        return output

    if not os.path.isfile(model_path):
        output = "model_path is not a file: "+ model_path
        util.printD(output)
        return output

    model_folder = os.path.dirname(model_path)

    new_model_path = downloader.dl(download_url, model_folder, None, None)
    if not new_model_path:
        output = "Download failed, check console log for detail. Download url: " + download_url
        util.printD(output)
        return output

    version_info = civitai.get_version_info_by_version_id(version_id)
    if not version_info:
        output = "Model downloaded, but failed to get version info, check console log for detail. Model saved to: " + new_model_path
        util.printD(output)
        return output

    base, ext = os.path.splitext(new_model_path)
    info_file = base + civitai.suffix + model.info_ext
    model.write_model_info(info_file, version_info)

    civitai.get_preview_image_by_model_path(new_model_path, max_size_preview, skip_nsfw_preview)

    output = "Done. Model downloaded to: " + new_model_path
    util.printD(output)
    return output



def remove_model_by_path(msg):
    util.printD("Start remove_model_by_path")

    output = ""
    result = msg_handler.parse_js_msg(msg)
    if not result:
        output = "Parsing js ms failed"
        util.printD(output)
        return output

    model_type = result.get("model_type", "")
    search_term = ""
    model_path = ""


    if "model_path" in result.keys():
        model_path = result["model_path"]
    else:
        search_term = result.get("search_term", "")
        model_path = model.get_model_path_by_search_term(model_type, search_term)

    if not model_path:
        output = f"Fail to get model for {model_type} {search_term}"
        util.printD(output)
        return output

    if not os.path.isfile(model_path):
        output = f"Model {model_type} {search_term} does not exist, no need to remove"
        util.printD(output)
        return output

    related_paths = [model_path]

    base, ext = os.path.splitext(model_path)
    info_path = base + model.info_ext
    first_preview_path = base+".png"
    sec_preview_path = base+".preview.png"
    civitai_info_path = base + civitai.suffix + model.info_ext
    note_path = base + ".ch_note"

    for p in [civitai_info_path, first_preview_path, sec_preview_path, info_path, note_path]:
        if os.path.isfile(p):
            related_paths.append(p)

    for rp in related_paths:
        if os.path.isfile(rp):
            util.printD(f"Removing file {rp}")
            os.remove(rp)

    util.printD(f"{len(related_paths)} file removed")

    util.printD("End remove_model_by_path")
    return output


def _get_lora_name(search_term, model_path):
    if search_term:
        parts = search_term.split()
        filename = parts[0] if parts else ""
        return os.path.splitext(os.path.basename(filename))[0]
    elif model_path:
        return os.path.splitext(os.path.basename(model_path))[0]
    return ""


def apply_lora_with_strength(msg):
    util.printD("Start apply_lora_with_strength")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return

    prompt = result.get("prompt", "")
    strength = result.get("strength", 1.0)
    model_info, model_type, search_term, model_path = _load_model_info_from_msg(result)

    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, prompt]

    lora_name = _get_lora_name(search_term, model_path)
    trainedWords = model_info.get("trainedWords", [])
    trigger_words = ", ".join(trainedWords) if trainedWords else ""
    lora_tag = f"<lora:{lora_name}:{strength}>" if lora_name else ""

    if trigger_words and lora_tag:
        new_prompt = prompt + " " + trigger_words + " " + lora_tag
    elif trigger_words:
        new_prompt = prompt + " " + trigger_words
    elif lora_tag:
        new_prompt = prompt + " " + lora_tag
    else:
        new_prompt = prompt

    util.printD(f"Applied LoRA with strength {strength}: {lora_name}")
    util.printD(f"new_prompt: {new_prompt}")

    return [new_prompt, new_prompt]


def get_trigger_words(msg):
    util.printD("Start get_trigger_words")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return msg_handler.build_py_msg("get_trigger_words", {"trigger_words": []})

    model_info, model_type, search_term, model_path = _load_model_info_from_msg(result)

    trigger_words = []
    if model_info:
        trainedWords = model_info.get("trainedWords", [])
        if trainedWords:
            trigger_words = trainedWords

    util.printD(f"Trigger words: {trigger_words}")
    return msg_handler.build_py_msg("get_trigger_words", {"trigger_words": trigger_words})


def get_model_file_size(msg):
    util.printD("Start get_model_file_size")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return msg_handler.build_py_msg("get_model_file_size", {"file_size": 0})

    model_type = result.get("model_type", "")
    search_term = ""
    model_path = ""
    file_size = 0

    if "model_path" in result.keys():
        model_path = result["model_path"]
    else:
        search_term = result.get("search_term", "")
        model_path = model.get_model_path_by_search_term(model_type, search_term)

    if model_path and os.path.isfile(model_path):
        file_size = os.path.getsize(model_path)

    util.printD(f"Model file size: {file_size}")
    return msg_handler.build_py_msg("get_model_file_size", {"file_size": file_size})


def save_model_note(msg):
    util.printD("Start save_model_note")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return "Failed to save note"

    model_type = result.get("model_type", "")
    search_term = ""
    model_path = ""
    note = result.get("note", "")

    if "model_path" in result.keys():
        model_path = result["model_path"]
    else:
        search_term = result.get("search_term", "")
        model_path = model.get_model_path_by_search_term(model_type, search_term)

    if not model_path:
        return "Failed to find model file"

    base, ext = os.path.splitext(model_path)
    note_path = base + ".ch_note"

    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note)
        util.printD(f"Note saved to: {note_path}")
        return "Note saved"
    except Exception as e:
        util.printD(f"Failed to save note: {str(e)}")
        return f"Failed to save note: {str(e)}"


def batch_get_model_data(msg):
    util.printD("Start batch_get_model_data")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return msg_handler.build_py_msg("batch_get_model_data", {"items": []})

    model_type = result.get("model_type", "")
    search_terms = result.get("search_terms", [])

    items = []
    for search_term in search_terms:
        model_path = model.get_model_path_by_search_term(model_type, search_term)

        trigger_words = []
        file_size = 0
        note = ""

        if model_path:
            if os.path.isfile(model_path):
                file_size = os.path.getsize(model_path)

            model_info = civitai.load_model_info_by_search_term(model_type, search_term)
            if model_info:
                trainedWords = model_info.get("trainedWords", [])
                if trainedWords:
                    trigger_words = trainedWords

            base, ext = os.path.splitext(model_path)
            note_path = base + ".ch_note"
            if os.path.isfile(note_path):
                try:
                    with open(note_path, 'r', encoding='utf-8') as f:
                        note = f.read().strip()
                except Exception:
                    pass

        items.append({
            "search_term": search_term,
            "trigger_words": trigger_words,
            "file_size": file_size,
            "note": note,
        })

    util.printD(f"Batch fetched data for {len(items)} models")
    return msg_handler.build_py_msg("batch_get_model_data", {"items": items})


def _validate_ext_path(ext_name, ext_path):
    extensions_dir = os.path.join(root_path, "extensions")
    real_ext_path = os.path.realpath(ext_path)
    real_extensions_dir = os.path.realpath(extensions_dir)
    if not real_ext_path.startswith(real_extensions_dir):
        util.printD(f"Path traversal detected: {ext_path} is outside extensions directory")
        return False
    if ".." in ext_name or "/" in ext_name or "\\" in ext_name:
        util.printD(f"Invalid extension name: {ext_name}")
        return False
    return True


def uninstall_extension(msg):
    util.printD("Start uninstall_extension")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return "Failed to uninstall: parsing message failed"

    ext_name = result.get("extension_name", "")
    if not ext_name:
        return "Failed to uninstall: extension name is empty"

    extensions_dir = os.path.join(root_path, "extensions")
    ext_path = os.path.join(extensions_dir, ext_name)

    if not _validate_ext_path(ext_name, ext_path):
        return "Failed to uninstall: invalid extension path"

    if not os.path.isdir(ext_path):
        return f"Failed to uninstall: extension folder not found: {ext_path}"

    try:
        import shutil
        shutil.rmtree(ext_path)
        util.printD(f"Extension uninstalled: {ext_path}")
        return f"Extension '{ext_name}' uninstalled successfully. Please restart the UI."
    except Exception as e:
        util.printD(f"Failed to uninstall extension: {str(e)}")
        return f"Failed to uninstall: {str(e)}"


def force_update_extension(msg):
    util.printD("Start force_update_extension")

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js msg failed")
        return "Failed to update: parsing message failed"

    ext_name = result.get("extension_name", "")
    if not ext_name:
        return "Failed to update: extension name is empty"

    extensions_dir = os.path.join(root_path, "extensions")
    ext_path = os.path.join(extensions_dir, ext_name)

    if not _validate_ext_path(ext_name, ext_path):
        return "Failed to update: invalid extension path"

    if not os.path.isdir(ext_path):
        return f"Failed to update: extension folder not found: {ext_path}"

    import subprocess
    for branch in ["main", "master"]:
        try:
            subprocess.run(["git", "fetch", "origin"], cwd=ext_path, check=True, capture_output=True)
            subprocess.run(["git", "reset", "--hard", f"origin/{branch}"], cwd=ext_path, check=True, capture_output=True)
            subprocess.run(["git", "pull"], cwd=ext_path, check=True, capture_output=True)
            util.printD(f"Extension force updated ({branch} branch): {ext_path}")
            return f"Extension '{ext_name}' updated successfully ({branch} branch). Please restart the UI."
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)
            util.printD(f"Failed to force update extension ({branch}): {error_msg}")
            continue
        except Exception as e:
            util.printD(f"Failed to force update extension: {str(e)}")
            return f"Failed to update: {str(e)}"

    return "Failed to update: could not reset to either 'main' or 'master' branch"
