# -*- coding: UTF-8 -*-
import modules.scripts as scripts
import gradio as gr
import os
import modules
from modules import script_callbacks
from modules import shared
from scripts.ch_lib import model
from scripts.ch_lib import js_action_civitai
from scripts.ch_lib import model_action_civitai
from scripts.ch_lib import civitai
from scripts.ch_lib import util
from scripts.ch_lib import msg_handler
from scripts.ch_lib import downloader


root_path = os.getcwd()
extension_path = scripts.basedir()

model.get_custom_model_folder()

_settings_registered = False


def on_ui_settings():
    global _settings_registered
    if _settings_registered:
        return
    _settings_registered = True

    ch_section = ("civitai_helper", "Civitai Helper")
    shared.opts.add_option("ch_max_size_preview", shared.OptionInfo(True, "Download Max Size Preview", gr.Checkbox, {"interactive": True}, section=ch_section))
    shared.opts.add_option("ch_skip_nsfw_preview", shared.OptionInfo(False, "Skip NSFW Preview Images", gr.Checkbox, {"interactive": True}, section=ch_section))
    shared.opts.add_option("ch_open_url_with_js", shared.OptionInfo(True, "Open Url At Client Side", gr.Checkbox, {"interactive": True}, section=ch_section))
    shared.opts.add_option("ch_check_new_ver_exist_in_all_folder", shared.OptionInfo(True, "When checking new model version, check new version existing in all model folders", gr.Checkbox, {"interactive": True}, section=ch_section))
    shared.opts.add_option("ch_proxy", shared.OptionInfo("", "Civitai Helper Proxy", gr.Textbox, {"interactive": True, "lines":1, "info":"format: socks5h://127.0.0.1:port"}, section=ch_section))
    shared.opts.add_option("ch_civiai_api_key", shared.OptionInfo("", "Civitai API Key", gr.Textbox, {"interactive": True, "lines":1, "info":"check doc:https://github.com/zixaphir/Stable-Diffusion-Webui-Civitai-Helper/tree/master#api-key"}, section=ch_section))
    shared.opts.add_option("ch_civitai_domain", shared.OptionInfo("civitai.red", "Civitai Domain", gr.Radio, {"interactive": True, "choices": ["civitai.red", "civitai.com"]}, section=ch_section))
    shared.opts.add_option("ch_lora_strength", shared.OptionInfo(1.0, "Default LoRA Strength", gr.Slider, {"interactive": True, "minimum": 0.0, "maximum": 2.0, "step": 0.05}, section=ch_section))

def on_ui_tabs():
    # Build UI tab — Forge calls this once per UI load; no guard needed

    try:
        txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
        txt2img_neg_prompt = modules.ui.txt2img_paste_fields[1][0]
        img2img_prompt = modules.ui.img2img_paste_fields[0][0]
        img2img_neg_prompt = modules.ui.img2img_paste_fields[1][0]
    except (IndexError, AttributeError, TypeError) as e:
        util.printD(f"Failed to access paste_fields, using fallback: {str(e)}")
        txt2img_prompt = None
        txt2img_neg_prompt = None
        img2img_prompt = None
        img2img_neg_prompt = None

    max_size_preview = shared.opts.data.get("ch_max_size_preview", True)
    skip_nsfw_preview = shared.opts.data.get("ch_skip_nsfw_preview", False)
    open_url_with_js = shared.opts.data.get("ch_open_url_with_js", True)
    check_new_ver_exist_in_all_folder = shared.opts.data.get("ch_check_new_ver_exist_in_all_folder", False)
    proxy = shared.opts.data.get("ch_proxy", "")
    civitai_api_key = shared.opts.data.get("ch_civiai_api_key", "")
    civitai_domain = shared.opts.data.get("ch_civitai_domain", "civitai.red")

    util.printD("Settings:")
    util.printD("max_size_preview: " + str(max_size_preview))
    util.printD("skip_nsfw_preview: " + str(skip_nsfw_preview))
    util.printD("open_url_with_js: " + str(open_url_with_js))
    util.printD("check_new_ver_exist_in_all_folder: " + str(check_new_ver_exist_in_all_folder))
    util.printD("proxy: " + str(proxy))

    has_api_key = False
    if civitai_api_key:
        has_api_key = True
        util.civitai_api_key = civitai_api_key
        util.def_headers["Authorization"] = f"Bearer {civitai_api_key}"

    util.printD(f"use civitai api key: {has_api_key}")

    util.civitai_domain = civitai_domain
    util.printD(f"civitai domain: {util.civitai_domain}")

    if proxy:
        util.proxies = {
            "http": proxy,
            "https": proxy,
        }


    def scan_model_gen(scan_model_types, force_overwrite):
        yield from model_action_civitai.scan_model(scan_model_types, max_size_preview, skip_nsfw_preview, force_overwrite)

    def get_model_info_by_input(model_type_drop, model_name_drop, model_url_or_id_txtbox):
        return model_action_civitai.get_model_info_by_input(model_type_drop, model_name_drop, model_url_or_id_txtbox, max_size_preview, skip_nsfw_preview)

    def dl_model_by_input(dl_model_info, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop, dl_all_ckb):
        return model_action_civitai.dl_model_by_input(dl_model_info, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop, dl_all_ckb, max_size_preview, skip_nsfw_preview)

    def check_models_new_version_to_md(model_types):
        return model_action_civitai.check_models_new_version_to_md(model_types, check_new_ver_exist_in_all_folder)

    def open_model_url(js_msg_txtbox):
        return js_action_civitai.open_model_url(js_msg_txtbox, open_url_with_js)

    def dl_model_new_version(js_msg_txtbox):
        return js_action_civitai.dl_model_new_version(js_msg_txtbox, max_size_preview, skip_nsfw_preview)

    def batch_dl_new_versions(js_msg_txtbox):
        util.printD("Start batch_dl_new_versions")
        result = msg_handler.parse_js_msg(js_msg_txtbox)
        if not result:
            return "\u274c Failed to parse batch download request"
        versions = result.get("versions", [])
        if not versions:
            return "\u26a0 No versions to download"
        downloaded = 0
        failed = 0
        for v in versions:
            model_path = v.get("model_path", "")
            download_url = v.get("download_url", "")
            version_id = v.get("version_id", "")
            if not model_path or not download_url:
                failed += 1
                continue
            model_folder = os.path.dirname(model_path)
            new_path = downloader.dl(download_url, model_folder, None, None)
            if new_path:
                downloaded += 1
                if version_id:
                    version_info = civitai.get_version_info_by_version_id(str(version_id))
                    if version_info:
                        base, ext = os.path.splitext(new_path)
                        info_file = base + civitai.suffix + model.info_ext
                        model.write_model_info(info_file, version_info)
            else:
                failed += 1
        return f"\u2705 Batch download done. Downloaded: **{downloaded}**, Failed: **{failed}**"

    def get_model_names_by_input(model_type, empty_info_only):
        names = civitai.get_model_names_by_input(model_type, empty_info_only)
        return model_name_drop.update(choices=names)

    def get_model_info_by_url(url):
        r = model_action_civitai.get_model_info_by_url(url)

        model_info = {}
        model_name = ""
        model_type = ""
        subfolders = []
        version_strs = []
        if r:
            model_info, model_name, model_type, subfolders, version_strs = r

        return [model_info, model_name, model_type, dl_subfolder_drop.update(choices=subfolders), dl_version_drop.update(choices=version_strs)]

    with gr.Blocks(analytics_enabled=False, elem_id="civitai_helper_tab") as civitai_helper:

        model_types = list(model.folders.keys())
        no_info_model_names = civitai.get_model_names_by_input("ckp", False)

        dl_model_info = gr.State({})



        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Scan Models for Civitai")
                with gr.Row():
                    scan_model_types_ckbg = gr.CheckboxGroup(choices=model_types, label="Model Types", value=["lora"])
                with gr.Row():
                    scan_force_overwrite_ckb = gr.Checkbox(label="Force Overwrite (re-fetch all model info and preview images)", value=False, elem_id="ch_scan_force_overwrite_ckb")
                gr.Markdown(value="Models that already have both info file and preview image will be **automatically skipped** to save time.\nEnable **Force Overwrite** to re-fetch all info from Civitai (useful for updating Trigger Words etc.)")

                scan_model_civitai_btn = gr.Button(value="Scan", variant="primary", elem_id="ch_scan_model_civitai_btn")
                scan_model_log_md = gr.Markdown(value="Scanning takes time, just wait. Check console log for detail", elem_id="ch_scan_model_log_md")


        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Get Model Info from Civitai by URL")
                gr.Markdown("Use this when scanning can not find a local model on civitai")
                with gr.Row():
                    model_type_drop = gr.Dropdown(choices=model_types, label="Model Type", value="ckp", multiselect=False)
                    empty_info_only_ckb = gr.Checkbox(label="Only Show Models have no Info", value=False, elem_id="ch_empty_info_only_ckb", elem_classes="ch_vpadding")
                    model_name_drop = gr.Dropdown(choices=no_info_model_names, label="Model", value="ckp", multiselect=False)

                model_url_or_id_txtbox = gr.Textbox(label="Civitai URL", lines=1, value="")
                get_civitai_model_info_by_id_btn = gr.Button(value="Get Model Info from Civitai", variant="primary")
                get_model_by_id_log_md = gr.Markdown("")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Download Model")
                with gr.Row():
                    dl_model_url_or_id_txtbox = gr.Textbox(label="Civitai URL", lines=1, value="")
                    dl_model_info_btn = gr.Button(value="1. Get Model Info by Civitai Url", variant="primary")

                gr.Markdown(value="2. Pick Subfolder and Model Version")
                with gr.Row():
                    dl_model_name_txtbox = gr.Textbox(label="Model Name", interactive=False, lines=1, value="")
                    dl_model_type_txtbox = gr.Textbox(label="Model Type", interactive=False, lines=1, value="")
                    dl_subfolder_drop = gr.Dropdown(choices=[], label="Sub-folder", value="", interactive=True, multiselect=False)
                    dl_version_drop = gr.Dropdown(choices=[], label="Model Version", value="", interactive=True, multiselect=False)
                    dl_all_ckb = gr.Checkbox(label="Download All files", value=False, elem_id="ch_dl_all_ckb", elem_classes="ch_vpadding")

                dl_civitai_model_by_id_btn = gr.Button(value="3. Download Model", variant="primary")
                dl_log_md = gr.Markdown(value="Check Console log for Downloading Status")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Check models' new version")
                with gr.Row():
                    model_types_ckbg = gr.CheckboxGroup(choices=model_types, label="Model Types", value=["lora"])
                    check_models_new_version_btn = gr.Button(value="Check New Version from Civitai", variant="primary")

                check_models_new_version_log_md = gr.HTML("It takes time, just wait. Check console log for detail")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### LoRA Quick Apply")
                with gr.Row():
                    lora_strength_slider = gr.Slider(minimum=0.0, maximum=2.0, step=0.05, value=1.0, label="LoRA Strength", elem_id="ch_lora_strength", interactive=True)
                gr.Markdown(value="Set the default LoRA strength for the ⚡ button on LoRA cards")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Other")
                gr.Markdown(value="Settings are moved into Settings Tab->Civitai Helper section")


        gr.Markdown(f"<center>version:{util.version}</center>")

        js_msg_txtbox = gr.Textbox(label="Request Msg From Js", visible=False, lines=1, value="", elem_id="ch_js_msg_txtbox")
        py_msg_txtbox = gr.Textbox(label="Response Msg From Python", visible=False, lines=1, value="", elem_id="ch_py_msg_txtbox")

        js_open_url_btn = gr.Button(value="Open Model Url", visible=False, elem_id="ch_js_open_url_btn")
        js_add_trigger_words_btn = gr.Button(value="Add Trigger Words", visible=False, elem_id="ch_js_add_trigger_words_btn")
        js_use_preview_prompt_btn = gr.Button(value="Use Prompt from Preview Image", visible=False, elem_id="ch_js_use_preview_prompt_btn")
        js_dl_model_new_version_btn = gr.Button(value="Download Model's new version", visible=False, elem_id="ch_js_dl_model_new_version_btn")
        js_remove_card_btn = gr.Button(value="Remove Card", visible=False, elem_id="ch_js_remove_card_btn")
        js_apply_lora_btn = gr.Button(value="Apply LoRA", visible=False, elem_id="ch_js_apply_lora_btn")
        js_batch_dl_new_versions_btn = gr.Button(value="Batch Download New Versions", visible=False, elem_id="ch_js_batch_dl_new_versions_btn")
        js_save_note_btn = gr.Button(value="Save Note", visible=False, elem_id="ch_js_save_note_btn")
        js_get_trigger_words_btn = gr.Button(value="Get Trigger Words", visible=False, elem_id="ch_js_get_trigger_words_btn")
        js_get_file_size_btn = gr.Button(value="Get File Size", visible=False, elem_id="ch_js_get_file_size_btn")
        js_batch_fetch_btn = gr.Button(value="Batch Fetch Model Data", visible=False, elem_id="ch_js_batch_fetch_btn")
        js_uninstall_ext_btn = gr.Button(value="Uninstall Extension", visible=False, elem_id="ch_js_uninstall_ext_btn")
        js_force_update_ext_btn = gr.Button(value="Force Update Extension", visible=False, elem_id="ch_js_force_update_ext_btn")

        scan_model_civitai_btn.click(scan_model_gen, inputs=[scan_model_types_ckbg, scan_force_overwrite_ckb], outputs=scan_model_log_md)

        model_type_drop.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)
        empty_info_only_ckb.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)

        get_civitai_model_info_by_id_btn.click(get_model_info_by_input, inputs=[model_type_drop, model_name_drop, model_url_or_id_txtbox], outputs=get_model_by_id_log_md)

        dl_model_info_btn.click(get_model_info_by_url, inputs=dl_model_url_or_id_txtbox, outputs=[dl_model_info, dl_model_name_txtbox, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop])
        dl_civitai_model_by_id_btn.click(dl_model_by_input, inputs=[dl_model_info, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop, dl_all_ckb], outputs=dl_log_md)

        check_models_new_version_btn.click(check_models_new_version_to_md, inputs=model_types_ckbg, outputs=check_models_new_version_log_md)

        js_open_url_btn.click(open_model_url, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_add_trigger_words_btn.click(js_action_civitai.add_trigger_words, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_use_preview_prompt_btn.click(js_action_civitai.use_preview_image_prompt, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, txt2img_neg_prompt, img2img_prompt, img2img_neg_prompt])
        js_dl_model_new_version_btn.click(dl_model_new_version, inputs=[js_msg_txtbox], outputs=dl_log_md)
        js_remove_card_btn.click(js_action_civitai.remove_model_by_path, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_apply_lora_btn.click(js_action_civitai.apply_lora_with_strength, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_batch_dl_new_versions_btn.click(batch_dl_new_versions, inputs=[js_msg_txtbox], outputs=dl_log_md)
        js_save_note_btn.click(js_action_civitai.save_model_note, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_get_trigger_words_btn.click(js_action_civitai.get_trigger_words, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_get_file_size_btn.click(js_action_civitai.get_model_file_size, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_batch_fetch_btn.click(js_action_civitai.batch_get_model_data, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_uninstall_ext_btn.click(js_action_civitai.uninstall_extension, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)
        js_force_update_ext_btn.click(js_action_civitai.force_update_extension, inputs=[js_msg_txtbox], outputs=py_msg_txtbox)

    return (civitai_helper , "Civitai Helper", "civitai_helper"),


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)


