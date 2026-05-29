# -*- coding: UTF-8 -*-
import os
import time
from . import util
from . import model
from . import civitai
from . import downloader


MAX_TABLE_ROWS = 50


def scan_model(scan_model_types, max_size_preview, skip_nsfw_preview, force_overwrite=False):
    util.printD("Start scan_model")

    if not scan_model_types:
        output = "Model Types is None, can not scan."
        util.printD(output)
        yield output
        return

    model_types = []
    if type(scan_model_types) == str:
        model_types.append(scan_model_types)
    else:
        model_types = scan_model_types

    all_models = []
    for model_type, model_folder in model.folders.items():
        if model_type not in model_types:
            continue
        try:
            for root, dirs, files in os.walk(model_folder, followlinks=True):
                for filename in files:
                    item = os.path.join(root, filename)
                    base, ext = os.path.splitext(item)
                    if ext in model.exts:
                        if len(base) > 4:
                            if base[-4:] == model.vae_suffix:
                                continue
                        all_models.append((model_type, item, filename))
        except Exception as e:
            util.printD(f"Error scanning folder {model_folder}: {str(e)}")

    total = len(all_models)
    if total == 0:
        yield "No models found to scan."
        return

    if force_overwrite:
        yield f"🔍 Found **{total}** models. **Force Overwrite** mode - re-fetching all model info...\n\n| Step | Model | Status |\n|------|-------|--------|"
    else:
        yield f"🔍 Found **{total}** models to scan. Starting...\n\n| Step | Model | Status |\n|------|-------|--------|"

    model_count = 0
    image_count = 0
    skipped_count = 0
    table_rows = []

    for idx, (model_type, item, filename) in enumerate(all_models):
        try:
            current = idx + 1
            base, ext = os.path.splitext(item)

            if not force_overwrite and model.has_info_and_preview(item):
                skipped_count = skipped_count + 1
                table_rows.append(f"| {current}/{total} | {filename} | ⏭ Skipped (complete) |")
                if current % 10 == 0 or current == total:
                    progress_pct = int(current / total * 100)
                    display_rows = table_rows[-MAX_TABLE_ROWS:]
                    yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)
                continue

            info_file = base + civitai.suffix + model.info_ext
            need_fetch_info = force_overwrite or not os.path.isfile(info_file)

            if need_fetch_info:
                table_rows.append(f"| {current}/{total} | {filename} | 🔐 Computing SHA256... |")
                progress_pct = int(current / total * 100)
                display_rows = table_rows[-MAX_TABLE_ROWS:]
                yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)

                hash = util.gen_file_sha256(item)

                if not hash:
                    table_rows[-1] = f"| {current}/{total} | {filename} | ❌ SHA256 failed |"
                    display_rows = table_rows[-MAX_TABLE_ROWS:]
                    yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)
                    continue

                model_info = civitai.get_model_info_by_hash(hash)
                if model_type == "ti":
                    util.printD("Delay 1 second for TI")
                    time.sleep(1)

                if model_info is None:
                    table_rows[-1] = f"| {current}/{total} | {filename} | ❌ API failed |"
                    display_rows = table_rows[-MAX_TABLE_ROWS:]
                    yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)
                    continue

                model.write_model_info(info_file, model_info)
                table_rows[-1] = f"| {current}/{total} | {filename} | ✅ Info fetched |"

            model_count = model_count + 1

            need_preview = force_overwrite or not model._has_preview(item)
            if need_preview:
                table_rows.append(f"| {current}/{total} | {filename} | 🖼 Downloading preview... |")
                progress_pct = int(current / total * 100)
                display_rows = table_rows[-MAX_TABLE_ROWS:]
                yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)

                civitai.get_preview_image_by_model_path(item, max_size_preview, skip_nsfw_preview)
                image_count = image_count + 1

                table_rows[-1] = f"| {current}/{total} | {filename} | ✅ Preview downloaded |"
            else:
                table_rows.append(f"| {current}/{total} | {filename} | ⏭ Preview exists |")

            progress_pct = int(current / total * 100)
            display_rows = table_rows[-MAX_TABLE_ROWS:]
            yield f"🔍 Scanning... **{progress_pct}%** ({current}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)

        except Exception as e:
            util.printD(f"Error processing model {filename}: {str(e)}")
            table_rows.append(f"| {idx+1}/{total} | {filename} | ❌ Error: {str(e)} |")
            progress_pct = int((idx + 1) / total * 100)
            display_rows = table_rows[-MAX_TABLE_ROWS:]
            yield f"🔍 Scanning... **{progress_pct}%** ({idx+1}/{total}) | Scanned: {model_count} | Skipped: {skipped_count}\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)

    display_rows = table_rows[-MAX_TABLE_ROWS:]
    yield f"✅ **Done!** Scanned: **{model_count}** | Images: **{image_count}** | Skipped: **{skipped_count}** | Total: **{total}**\n\n| Step | Model | Status |\n|------|-------|--------|\n" + "\n".join(display_rows)

    util.printD(f"Done. Scanned {model_count} models, checked {image_count} images, skipped {skipped_count} complete models")


def get_model_info_by_input(model_type, model_name, model_url_or_id, max_size_preview, skip_nsfw_preview):
    util.printD("Start get_model_info_by_input")

    if not model_type:
        return "Model Type can not be empty"

    if not model_name and not model_url_or_id:
        return "Model Name or URL can not be empty"

    if model_url_or_id:
        model_id = civitai.get_model_id_from_url(model_url_or_id)
        if not model_id:
            return "Can not get model id from URL"

        model_info = civitai.get_model_info_by_id(model_id)
        if not model_info:
            return "Failed to get model info from Civitai"

        subfolders = util.get_subfolders(model.folders[model_type])
        if subfolders is None:
            subfolders = []
        subfolders = [""] + subfolders

        version_strs = []
        if "modelVersions" in model_info.keys():
            for version in model_info["modelVersions"]:
                if "name" in version.keys():
                    version_strs.append(version["name"])

        return [model_info, model_type, subfolders, version_strs]

    r = model.get_model_path_by_type_and_name(model_type, model_name)
    if not r:
        return f"Can not find model: {model_type} {model_name}"

    model_root, model_path = r
    base, ext = os.path.splitext(model_path)
    info_file = base + civitai.suffix + model.info_ext

    if os.path.isfile(info_file):
        model_info = model.load_model_info(info_file)
        if not model_info:
            return f"Failed to load model info from: {info_file}"

        if "id" not in model_info.keys():
            return f"Model info file has no id, try to get model info from Civitai by hash"

        version_id = model_info["id"]
        version_info = civitai.get_version_info_by_version_id(str(version_id))
        if not version_info:
            return f"Failed to get version info from Civitai"

        model.write_model_info(info_file, version_info)
        civitai.get_preview_image_by_model_path(model_path, max_size_preview, skip_nsfw_preview)
        return f"Model info updated for: {model_name}"

    hash = util.gen_file_sha256(model_path)
    if not hash:
        return f"Failed to compute SHA256 for: {model_name}"

    model_info = civitai.get_model_info_by_hash(hash)
    if not model_info:
        return f"Can not find this model on Civitai: {model_name}"

    model.write_model_info(info_file, model_info)
    civitai.get_preview_image_by_model_path(model_path, max_size_preview, skip_nsfw_preview)
    return f"Model info fetched for: {model_name}"


def get_model_info_by_url(url):
    util.printD("Start get_model_info_by_url")

    if not url:
        return

    model_id = civitai.get_model_id_from_url(url)
    if not model_id:
        return

    model_info = civitai.get_model_info_by_id(model_id)
    if not model_info:
        return

    model_type_str = model_info.get("type", "")
    model_type = civitai.model_type_dict.get(model_type_str)
    if not model_type:
        util.printD(f"Unknow model type from civitai: {model_type_str}")
        return

    model_name = model_info.get("name", "")

    subfolders = util.get_subfolders(model.folders[model_type])
    if subfolders is None:
        subfolders = []
    subfolders = [""] + subfolders

    version_strs = []
    if "modelVersions" in model_info.keys():
        for version in model_info["modelVersions"]:
            if "name" in version.keys():
                version_strs.append(version["name"])

    return (model_info, model_name, model_type, subfolders, version_strs)


def dl_model_by_input(dl_model_info, dl_model_type, dl_subfolder, dl_version, dl_all, max_size_preview, skip_nsfw_preview):
    util.printD("Start dl_model_by_input")

    if not dl_model_info:
        return "No model info, please get model info first"

    if not dl_model_type:
        return "Model type can not be empty"

    if dl_model_type not in model.folders.keys():
        return f"Unknow model type: {dl_model_type}"

    if not dl_version:
        return "Please select a model version"

    if not dl_model_info.get("modelVersions"):
        return "No model versions found"

    version_info = None
    for version in dl_model_info["modelVersions"]:
        if version.get("name") == dl_version:
            version_info = version
            break

    if not version_info:
        return f"Can not find version: {dl_version}"

    download_url = version_info.get("downloadUrl", "")
    if not download_url:
        return "No download URL found for this version"

    model_folder = model.folders[dl_model_type]
    if dl_subfolder:
        model_folder = os.path.join(model_folder, dl_subfolder)

    if not os.path.isdir(model_folder):
        os.makedirs(model_folder, exist_ok=True)

    files = version_info.get("files", [])
    if dl_all and files:
        for file_info in files:
            file_url = file_info.get("downloadUrl", "")
            file_name = file_info.get("name", "")
            if file_url:
                result = downloader.dl(file_url, model_folder, file_name, None)
                if not result:
                    util.printD(f"Failed to download file: {file_name}")
    else:
        result = downloader.dl(download_url, model_folder, None, None)
        if not result:
            return "Download failed, check console log for detail"

    version_id = version_info.get("id")
    if version_id:
        version_detail = civitai.get_version_info_by_version_id(str(version_id))
        if version_detail:
            model_name = dl_model_info.get("name", "unknown")
            safe_name = "".join(c for c in model_name if c.isalnum() or c in " _-").strip()
            info_filename = safe_name + civitai.suffix + model.info_ext
            info_path = os.path.join(model_folder, info_filename)
            model.write_model_info(info_path, version_detail)

    return "Download completed. Check console log for detail"


def check_models_new_version_to_md(model_types, check_new_ver_exist_in_all_folder):
    util.printD("Start check_models_new_version_to_md")

    if not model_types:
        return "Model Types can not be empty"

    new_versions = civitai.check_models_new_version_by_model_types(model_types, 1, check_new_ver_exist_in_all_folder)

    if not new_versions:
        return "No new version found"

    md = f"Found **{len(new_versions)}** new version(s)\n\n"
    md += "| Model | Type | New Version | Download URL |\n"
    md += "|-------|------|-------------|--------------|\n"

    for r in new_versions:
        model_path, model_id, model_name, current_version_id, new_version_name, description, downloadUrl, img_url = r
        md += f"| {model_name} | {os.path.basename(os.path.dirname(model_path))} | {new_version_name} | [Download]({downloadUrl}) |\n"

    return md
