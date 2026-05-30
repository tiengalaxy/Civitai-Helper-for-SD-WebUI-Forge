"use strict";

const ch_model_data_cache = {};
let ch_request_lock = false;

function ch_convert_file_path_to_url(path){
    let prefix = "file=";
    let path_to_url = path.replaceAll('\\', '/');
    return prefix+path_to_url;
}

function ch_img_node_str(path){
    return `<img src='${ch_convert_file_path_to_url(path)}' style="width:24px"/>`;
}

function ch_sd_version() {
    let foot = gradioApp().getElementById("footer");
    if (!foot) { return null; }
    let versions = foot.querySelector(".versions");
    if (!versions) { return null; }
    let [webui_version] = versions.getElementsByTagName("a");
    if (!webui_version) { return null; }
    return extract_version(webui_version.innerHTML);
}

function extract_version(text) {
    if (!text) return null;
    let matches;
    if (text[0] == 'f')
        matches = text.match(/v\d+\.\d+\.\d+/);
    else
        matches = text.match(/\d+\.\d+\.\d+/);
    if (matches === null || matches.length == 0) { return null; }
    if (text[0] == 'f') return matches[0].substring(1);
    return matches[0];
}

function send_ch_py_msg(msg){
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    if (js_msg_txtbox && msg) {
        js_msg_txtbox.value = JSON.stringify(msg);
        js_msg_txtbox.dispatchEvent(new Event("input"));
    }
}

function get_ch_py_msg(){
    const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
    if (py_msg_txtbox && py_msg_txtbox.value) {
        return py_msg_txtbox.value;
    }
    return "";
}

const get_new_ch_py_msg = (max_count=5) => new Promise((resolve, reject) => {
    let count = 0;
    let new_msg = "";
    let find_msg = false;
    const interval = setInterval(() => {
        const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
        count++;
        if (py_msg_txtbox && py_msg_txtbox.value) {
            new_msg = py_msg_txtbox.value;
            if (new_msg != "") { find_msg = true; }
        }
        if (find_msg) {
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(new Event("input"));
            resolve(new_msg);
            clearInterval(interval);
        } else if (count > max_count) {
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(new Event("input"));
            reject('');
            clearInterval(interval);
        }
    }, 1000);
})

function getActiveTabType() {
    const currentTab = get_uiCurrentTabContent();
    if (!currentTab) return null;
    switch (currentTab.id) {
        case "tab_txt2img": return "txt2img";
        case "tab_img2img": return "img2img";
    }
    return null;
}

function getActivePrompt() {
    const currentTab = get_uiCurrentTabContent();
    if (!currentTab) return null;
    switch (currentTab.id) {
        case "tab_txt2img": return currentTab.querySelector("#txt2img_prompt textarea");
        case "tab_img2img": return currentTab.querySelector("#img2img_prompt textarea");
    }
    return null;
}

function getActiveNegativePrompt() {
    const currentTab = get_uiCurrentTabContent();
    if (!currentTab) return null;
    switch (currentTab.id) {
        case "tab_txt2img": return currentTab.querySelector("#txt2img_neg_prompt textarea");
        case "tab_img2img": return currentTab.querySelector("#img2img_neg_prompt textarea");
    }
    return null;
}

function convertModelTypeFromPyToJS(model_type) {
    switch (model_type) {
        case "ti": return "textual_inversion";
        case "hyper": return "hypernetworks";
        case "ckp": return "checkpoints";
        case "lora": return "lora";
        case "controlnet": return "controlnet";
        case "vae": return "vae";
        case "upscaler": return "upscaler";
    }
    return "";
}

function convertModelTypeFromJsToPy(js_model_type) {
    switch (js_model_type) {
        case "textual_inversion": return "ti";
        case "hypernetworks": return "hyper";
        case "checkpoints": return "ckp";
        case "lora": return "lora";
        case "controlnet": return "controlnet";
        case "vae": return "vae";
        case "upscaler": return "upscaler";
    }
    return "";
}

async function open_model_url(event, model_type, search_term){
    if (ch_request_lock) { event.stopPropagation(); event.preventDefault(); return; }
    ch_request_lock = true;
    let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");
    if (!js_open_url_btn) { ch_request_lock = false; return; }

    let msg = {
        "action": "open_url",
        "model_type": model_type,
        "search_term": search_term,
        "prompt": "",
        "neg_prompt": "",
    }
    send_ch_py_msg(msg);
    js_open_url_btn.click();
    event.stopPropagation();
    event.preventDefault();

    let new_py_msg = "";
    try {
        new_py_msg = await get_new_ch_py_msg();
    } catch (error) {}

    ch_request_lock = false;

    if (new_py_msg) {
        try {
            let py_msg_json = JSON.parse(new_py_msg);
            if (py_msg_json && py_msg_json.content && py_msg_json.content.url) {
                window.open(py_msg_json.content.url, "_blank");
            }
        } catch(e) {}
    }
}

function add_trigger_words(event, model_type, search_term){
    let js_add_trigger_words_btn = gradioApp().getElementById("ch_js_add_trigger_words_btn");
    if (!js_add_trigger_words_btn) { return; }

    let msg = {
        "action": "add_trigger_words",
        "model_type": model_type,
        "search_term": search_term,
        "prompt": "",
        "neg_prompt": "",
    }
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt ? act_prompt.value : "";
    send_ch_py_msg(msg);
    js_add_trigger_words_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

function use_preview_prompt(event, model_type, search_term){
    let js_use_preview_prompt_btn = gradioApp().getElementById("ch_js_use_preview_prompt_btn");
    if (!js_use_preview_prompt_btn) { return; }

    let msg = {
        "action": "use_preview_prompt",
        "model_type": model_type,
        "search_term": search_term,
        "prompt": "",
        "neg_prompt": "",
    }
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt ? act_prompt.value : "";
    let neg_prompt = getActiveNegativePrompt();
    msg["neg_prompt"] = neg_prompt ? neg_prompt.value : "";
    send_ch_py_msg(msg);
    js_use_preview_prompt_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

async function remove_card(event, model_type, search_term){
    if (ch_request_lock) { event.stopPropagation(); event.preventDefault(); return; }
    ch_request_lock = true;
    let js_remove_card_btn = gradioApp().getElementById("ch_js_remove_card_btn");
    if (!js_remove_card_btn) { ch_request_lock = false; return; }

    if (!confirm("\nConfirm to remove this model.\n\nCheck console log for detail.")) { ch_request_lock = false; return; }

    let msg = {
        "action": "remove_card",
        "model_type": model_type,
        "search_term": search_term,
        "prompt": "",
        "neg_prompt": "",
    }
    send_ch_py_msg(msg);
    js_remove_card_btn.click();
    event.stopPropagation();
    event.preventDefault();

    let new_py_msg = "";
    try {
        new_py_msg = await get_new_ch_py_msg();
    } catch (error) {
        new_py_msg = error;
    }

    ch_request_lock = false;

    let result = "Done";
    if (new_py_msg) { result = new_py_msg; }
    alert(result);

    if (result=="Done"){
        let active_tab = getActiveTabType();
        if (active_tab){
            let js_model_type = convertModelTypeFromPyToJS(model_type);
            if (!js_model_type){return;}
            let refresh_btn_id = active_tab + "_" + js_model_type + "_extra_refresh";
            let refresh_btn = gradioApp().getElementById(refresh_btn_id);
            if (refresh_btn){ refresh_btn.click(); }
        }
    }
}

async function open_model_url_with_path(event, model_type, model_path){
    if (ch_request_lock) { event.stopPropagation(); event.preventDefault(); return; }
    ch_request_lock = true;
    let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");
    if (!js_open_url_btn) { ch_request_lock = false; return; }

    let msg = {
        "action": "open_url",
        "model_type": model_type,
        "model_path": model_path,
        "prompt": "",
        "neg_prompt": "",
    }
    send_ch_py_msg(msg);
    js_open_url_btn.click();
    event.stopPropagation();
    event.preventDefault();

    let new_py_msg = "";
    try {
        new_py_msg = await get_new_ch_py_msg();
    } catch (error) {}

    ch_request_lock = false;

    if (new_py_msg) {
        try {
            let py_msg_json = JSON.parse(new_py_msg);
            if (py_msg_json && py_msg_json.content && py_msg_json.content.url) {
                window.open(py_msg_json.content.url, "_blank");
            }
        } catch(e) {}
    }
}

function add_trigger_words_with_path(event, model_type, model_path){
    let js_add_trigger_words_btn = gradioApp().getElementById("ch_js_add_trigger_words_btn");
    if (!js_add_trigger_words_btn) { return; }

    let msg = {
        "action": "add_trigger_words",
        "model_type": model_type,
        "model_path": model_path,
        "prompt": "",
        "neg_prompt": "",
    }
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt ? act_prompt.value : "";
    send_ch_py_msg(msg);
    js_add_trigger_words_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

function use_preview_prompt_with_path(event, model_type, model_path){
    let js_use_preview_prompt_btn = gradioApp().getElementById("ch_js_use_preview_prompt_btn");
    if (!js_use_preview_prompt_btn) { return; }

    let msg = {
        "action": "use_preview_prompt",
        "model_type": model_type,
        "model_path": model_path,
        "prompt": "",
        "neg_prompt": "",
    }
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt ? act_prompt.value : "";
    let neg_prompt = getActiveNegativePrompt();
    msg["neg_prompt"] = neg_prompt ? neg_prompt.value : "";
    send_ch_py_msg(msg);
    js_use_preview_prompt_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

async function remove_card_with_path(event, model_type, model_path){
    if (ch_request_lock) { event.stopPropagation(); event.preventDefault(); return; }
    ch_request_lock = true;
    let js_remove_card_btn = gradioApp().getElementById("ch_js_remove_card_btn");
    if (!js_remove_card_btn) { ch_request_lock = false; return; }

    if (!confirm("\nConfirm to remove this model.\n\nCheck console log for detail.")) { ch_request_lock = false; return; }

    let msg = {
        "action": "remove_card",
        "model_type": model_type,
        "model_path": model_path,
        "prompt": "",
        "neg_prompt": "",
    }
    send_ch_py_msg(msg);
    js_remove_card_btn.click();
    event.stopPropagation();
    event.preventDefault();

    let new_py_msg = "";
    try {
        new_py_msg = await get_new_ch_py_msg();
    } catch (error) {
        new_py_msg = error;
    }

    ch_request_lock = false;

    let result = "Done";
    if (new_py_msg) { result = new_py_msg; }
    alert(result);

    if (result=="Done"){
        let active_tab = getActiveTabType();
        if (active_tab){
            let js_model_type = convertModelTypeFromPyToJS(model_type);
            if (!js_model_type){return;}
            let refresh_btn_id = active_tab + "_" + js_model_type + "_extra_refresh";
            let refresh_btn = gradioApp().getElementById(refresh_btn_id);
            if (refresh_btn){ refresh_btn.click(); }
        }
    }
}

function ch_dl_model_new_version(event, model_path, version_id, download_url){
    if (!confirm("\nConfirm to download.\n\nCheck Download Model Section's log and console log for detail.")) { return; }

    let js_dl_model_new_version_btn = gradioApp().getElementById("ch_js_dl_model_new_version_btn");
    if (!js_dl_model_new_version_btn) { return; }

    let msg = {
        "action": "dl_model_new_version",
        "model_path": model_path,
        "version_id": version_id,
        "download_url": download_url,
    }
    send_ch_py_msg(msg);
    js_dl_model_new_version_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

function ch_apply_lora_with_strength(event, model_type, search_term){
    let js_apply_lora_btn = gradioApp().getElementById("ch_js_apply_lora_btn");
    if (!js_apply_lora_btn) { return; }

    let strength = 1.0;
    let strengthInput = gradioApp().querySelector("#ch_lora_strength input");
    if (strengthInput && strengthInput.value) {
        strength = parseFloat(strengthInput.value) || 1.0;
    }

    let msg = {
        "action": "apply_lora_with_strength",
        "model_type": model_type,
        "search_term": search_term,
        "strength": strength,
        "prompt": "",
        "neg_prompt": "",
    }
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt ? act_prompt.value : "";
    send_ch_py_msg(msg);
    js_apply_lora_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

function ch_batch_dl_new_versions(){
    let btn = gradioApp().getElementById("ch_js_batch_dl_new_versions_btn");
    if (!btn) { return; }

    let items = gradioApp().querySelectorAll(".ch-new-ver-dl-btn");
    if (!items || items.length == 0) {
        alert("No new versions to download");
        return;
    }

    if (!confirm(`\nConfirm to batch download ${items.length} new version(s)?\n\nCheck console log for detail.`)) { return; }

    btn.click();
}

function ch_save_model_note(event, model_type, search_term){
    let js_save_note_btn = gradioApp().getElementById("ch_js_save_note_btn");
    if (!js_save_note_btn) { return; }

    let card = event.target.closest(".card");
    let noteInput = card ? card.querySelector(".ch-note-input") : null;
    let note = noteInput ? noteInput.value : "";

    let msg = {
        "action": "save_note",
        "model_type": model_type,
        "search_term": search_term,
        "note": note,
    }
    send_ch_py_msg(msg);
    js_save_note_btn.click();
    event.stopPropagation();
    event.preventDefault();
}

function compareVersions(version1, version2) {
    const v1Parts = version1.split('.').map(Number);
    const v2Parts = version2.split('.').map(Number);
    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
        const v1Part = v1Parts[i] || 0;
        const v2Part = v2Parts[i] || 0;
        if (v1Part > v2Part) { return 1; }
        else if (v1Part < v2Part) { return -1; }
    }
    return 0;
}

function ch_format_file_size(bytes) {
    if (!bytes || bytes <= 0) return "";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + " GB";
}

async function ch_batch_fetch_model_data(model_type, search_terms) {
    let uncached = [];
    for (let st of search_terms) {
        let cache_key = model_type + "|" + st;
        if (ch_model_data_cache[cache_key]) continue;
        uncached.push(st);
    }

    if (uncached.length === 0) return;

    let js_batch_fetch_btn = gradioApp().getElementById("ch_js_batch_fetch_btn");
    if (!js_batch_fetch_btn) return;

    let msg = {
        "action": "batch_get_model_data",
        "model_type": model_type,
        "search_terms": uncached,
    };

    send_ch_py_msg(msg);
    js_batch_fetch_btn.click();

    try {
        let response = await get_new_ch_py_msg(10);
        if (response) {
            let py_msg_json = JSON.parse(response);
            if (py_msg_json && py_msg_json.content && py_msg_json.content.items) {
                for (let item of py_msg_json.content.items) {
                    let cache_key = model_type + "|" + item.search_term;
                    ch_model_data_cache[cache_key] = item;
                }
            }
        }
    } catch(e) {}
}

function ch_apply_cached_data_to_cards(cards, model_type) {
    for (let card of cards) {
        let search_term_node = card.querySelector(".actions .additional .search_term");
        if (!search_term_node) {
            search_term_node = card.querySelector(".actions .additional .search_terms");
        }
        if (!search_term_node) continue;

        let search_term = search_term_node.innerHTML.trim();
        if (!search_term) continue;

        let cache_key = model_type + "|" + search_term;
        let data = ch_model_data_cache[cache_key];
        if (!data) continue;

        if (data.trigger_words && data.trigger_words.length > 0 && !card.querySelector(".ch-trigger-tooltip")) {
            let tooltip = document.createElement("div");
            tooltip.className = "ch-trigger-tooltip";
            tooltip.innerHTML = "🔑 " + data.trigger_words.join(", ");
            card.appendChild(tooltip);
        }

        if (data.file_size > 0 && !card.querySelector(".ch-file-size")) {
            let sizeStr = ch_format_file_size(data.file_size);
            if (sizeStr) {
                let badge = document.createElement("span");
                badge.className = "ch-file-size";
                badge.innerHTML = sizeStr;
                let name_row = card.querySelector(".name");
                if (name_row) {
                    name_row.appendChild(badge);
                }
            }
        }
    }
}


onUiLoaded(() => {
    let tab_prefix_list = ["txt2img", "img2img"];
    let model_type_list = ["textual_inversion", "hypernetworks", "checkpoints", "lora", "controlnet", "vae", "upscaler"];
    let cardid_suffix = "cards";

    function create_card_buttons(model_type, search_term) {
        let buttons = [];

        let open_url_node = document.createElement("a");
        open_url_node.href = "#";
        open_url_node.innerHTML = "🌐";
        open_url_node.className = "card-button";
        open_url_node.title = "Open Civitai page";
        open_url_node.setAttribute("onclick","open_model_url(event, '"+model_type+"', '"+search_term+"')");
        buttons.push(open_url_node);

        let add_trigger_words_node = document.createElement("a");
        add_trigger_words_node.href = "#";
        add_trigger_words_node.innerHTML = "💡";
        add_trigger_words_node.className = "card-button";
        add_trigger_words_node.title = "Add trigger words to prompt";
        add_trigger_words_node.setAttribute("onclick","add_trigger_words(event, '"+model_type+"', '"+search_term+"')");
        buttons.push(add_trigger_words_node);

        let use_preview_prompt_node = document.createElement("a");
        use_preview_prompt_node.href = "#";
        use_preview_prompt_node.innerHTML = "🏷️";
        use_preview_prompt_node.className = "card-button";
        use_preview_prompt_node.title = "Use prompt from preview image";
        use_preview_prompt_node.setAttribute("onclick","use_preview_prompt(event, '"+model_type+"', '"+search_term+"')");
        buttons.push(use_preview_prompt_node);

        if (model_type === "lora") {
            let apply_lora_node = document.createElement("a");
            apply_lora_node.href = "#";
            apply_lora_node.innerHTML = "⚡";
            apply_lora_node.className = "card-button";
            apply_lora_node.title = "Apply LoRA with strength to prompt";
            apply_lora_node.setAttribute("onclick","ch_apply_lora_with_strength(event, '"+model_type+"', '"+search_term+"')");
            buttons.push(apply_lora_node);
        }

        let note_node = document.createElement("a");
        note_node.href = "#";
        note_node.innerHTML = "📝";
        note_node.className = "card-button";
        note_node.title = "Edit note for this model";
        note_node.setAttribute("onclick","ch_toggle_model_note(event, '"+model_type+"', '"+search_term+"')");
        buttons.push(note_node);

        let remove_card_node = document.createElement("a");
        remove_card_node.href = "#";
        remove_card_node.innerHTML = "❌";
        remove_card_node.className = "card-button";
        remove_card_node.title = "Remove this model";
        remove_card_node.setAttribute("onclick","remove_card(event, '"+model_type+"', '"+search_term+"')");
        buttons.push(remove_card_node);

        return buttons;
    }

    function ch_toggle_model_note(event, model_type, search_term) {
        let card = event.target.closest(".card");
        if (!card) return;
        event.stopPropagation();
        event.preventDefault();

        let existing = card.querySelector(".ch-note-panel");
        if (existing) {
            existing.remove();
            return;
        }

        let panel = document.createElement("div");
        panel.className = "ch-note-panel";

        let textarea = document.createElement("textarea");
        textarea.className = "ch-note-input";
        textarea.placeholder = "Write your note here...";
        textarea.rows = 2;
        textarea.setAttribute("data-model-type", model_type);
        textarea.setAttribute("data-search-term", search_term);

        let cache_key = model_type + "|" + search_term;
        let cached = ch_model_data_cache[cache_key];
        if (cached && cached.note) {
            textarea.value = cached.note;
        }

        let save_btn = document.createElement("button");
        save_btn.innerHTML = "Save";
        save_btn.className = "ch-note-save-btn";
        save_btn.onclick = function(e) {
            e.stopPropagation();
            e.preventDefault();
            ch_save_model_note(e, model_type, search_term);
            if (ch_model_data_cache[cache_key]) {
                ch_model_data_cache[cache_key].note = textarea.value;
            }
            panel.remove();
        };

        textarea.addEventListener("click", function(e) { e.stopPropagation(); });
        textarea.addEventListener("input", function(e) { e.stopPropagation(); });

        panel.appendChild(textarea);
        panel.appendChild(save_btn);
        card.appendChild(panel);
    }

    function update_card_for_civitai(){
        let extra_network_id = "";
        let extra_network_node = null;
        let button_row = null;
        let search_term_node = null;
        let search_term = "";
        let model_type = "";
        let cards = null;

        let active_tab_type = getActiveTabType();
        if (!active_tab_type){active_tab_type = "txt2img";}

        for (const tab_prefix of tab_prefix_list) {
            if (tab_prefix != active_tab_type) {continue;}

            let active_extra_tab_type = "";
            let extra_tabs = gradioApp().getElementById(tab_prefix+"_extra_tabs");
            if (!extra_tabs) {continue;}

            const active_extra_tab = Array.from(get_uiCurrentTabContent().querySelectorAll('.extra-network-cards,.extra-network-thumbs'))
                .find(el => el.closest('.tabitem').style.display === 'block')
                ?.id.match(/^(txt2img|img2img)_(.+)_cards$/)?.[2];

            if (!active_extra_tab) continue;

            switch (active_extra_tab) {
                case "textual_inversion": active_extra_tab_type = "ti"; break;
                case "hypernetworks": active_extra_tab_type = "hyper"; break;
                case "checkpoints": active_extra_tab_type = "ckp"; break;
                case "lora": active_extra_tab_type = "lora"; break;
            }

            for (const js_model_type of model_type_list) {
                switch (js_model_type) {
                    case "textual_inversion": model_type = "ti"; break;
                    case "hypernetworks": model_type = "hyper"; break;
                    case "checkpoints": model_type = "ckp"; break;
                    case "lora": model_type = "lora"; break;
                }
                if (!model_type) { continue; }
                if (model_type != active_extra_tab_type) { continue; }

                extra_network_id = tab_prefix+"_"+js_model_type+"_"+cardid_suffix;
                extra_network_node = gradioApp().getElementById(extra_network_id);
                if (!extra_network_node) continue;

                cards = extra_network_node.querySelectorAll(".card");
                let search_terms_to_fetch = [];

                for (let card of cards) {
                    button_row = card.querySelector(".button-row");
                    if (!button_row){ continue; }

                    let atags = button_row.querySelectorAll("a");
                    if (atags && atags.length) {
                        ch_apply_cached_data_to_cards([card], model_type);
                        continue;
                    }

                    search_term_node = card.querySelector(".actions .additional .search_term");
                    if (!search_term_node){ continue; }

                    search_term = search_term_node.innerHTML.trim();
                    if (!search_term) { continue; }

                    let buttons = create_card_buttons(model_type, search_term);
                    for (let btn of buttons) {
                        button_row.appendChild(btn);
                    }

                    search_terms_to_fetch.push(search_term);
                }

                ch_apply_cached_data_to_cards(cards, model_type);

                if (search_terms_to_fetch.length > 0) {
                    ch_batch_fetch_model_data(model_type, search_terms_to_fetch).then(() => {
                        ch_apply_cached_data_to_cards(cards, model_type);
                    });
                }
            }
        }
    }


    function update_card_for_civitai_with_sd1_8(){
        let extra_network_id = "";
        let extra_network_node = null;
        let button_row = null;
        let search_term_node = null;
        let search_term = "";
        let model_type = "";
        let cards = null;
        let active_model_type = "";

        let active_tab_type = getActiveTabType();
        if (!active_tab_type){active_tab_type = "txt2img";}

        for (const tab_prefix of tab_prefix_list) {
            if (tab_prefix != active_tab_type) {continue;}

            for (const js_model_type of model_type_list) {
                let extra_tab = gradioApp().getElementById(tab_prefix+"_"+js_model_type);
                if (extra_tab == null){ continue; }
                if (extra_tab.style.display == "block"){
                    active_model_type = js_model_type;
                    break;
                }
            }

            if (!active_model_type) continue;

            switch (active_model_type) {
                case "textual_inversion": model_type = "ti"; break;
                case "hypernetworks": model_type = "hyper"; break;
                case "checkpoints": model_type = "ckp"; break;
                case "lora": model_type = "lora"; break;
            }

            if (!model_type) { continue; }

            extra_network_id = tab_prefix+"_"+active_model_type+"_"+cardid_suffix;
            extra_network_node = gradioApp().getElementById(extra_network_id);
            if (!extra_network_node) continue;

            cards = extra_network_node.querySelectorAll(".card");
            let search_terms_to_fetch = [];

            for (let card of cards) {
                button_row = card.querySelector(".button-row");
                if (!button_row){ continue; }
                button_row.style.flexWrap = "wrap";

                let atags = button_row.querySelectorAll("a");
                if (atags && atags.length) {
                    ch_apply_cached_data_to_cards([card], model_type);
                    continue;
                }

                search_term_node = card.querySelector(".actions .additional .search_terms");
                if (!search_term_node){ continue; }

                search_term = search_term_node.innerHTML.trim();
                if (!search_term) { continue; }

                let escaped_search_term = search_term.replaceAll("\\", "\\\\");

                let buttons = create_card_buttons(model_type, escaped_search_term);
                for (let btn of buttons) {
                    button_row.appendChild(btn);
                }

                search_terms_to_fetch.push(search_term);
            }

            ch_apply_cached_data_to_cards(cards, model_type);

            if (search_terms_to_fetch.length > 0) {
                ch_batch_fetch_model_data(model_type, search_terms_to_fetch).then(() => {
                    ch_apply_cached_data_to_cards(cards, model_type);
                });
            }
        }
    }


    let sd_version = ch_sd_version();
    let is_forge_or_new = !sd_version || compareVersions(sd_version, "1.8.0") >= 0;

    if (is_forge_or_new) {
        for (let prefix of tab_prefix_list) {
            for (const js_model_type of model_type_list) {
                let toolbar_id = prefix + "_" + js_model_type + "_controls";
                let extra_toolbar = gradioApp().getElementById(toolbar_id);
                let refresh_btn_id = prefix + "_" + js_model_type + "_extra_refresh";
                let refresh_btn = gradioApp().getElementById(refresh_btn_id);
                if (!refresh_btn) continue;
                if (!extra_toolbar) continue;

                let ch_refresh = document.createElement("button");
                ch_refresh.innerHTML = "🔁";
                ch_refresh.title = "Refresh Civitai Helper buttons";
                ch_refresh.className = "extra-network-control--refresh";
                ch_refresh.style.fontSize = "150%";
                ch_refresh.onclick = function(){
                    update_card_for_civitai_with_sd1_8();
                };

                extra_toolbar.style.gridTemplateColumns = "minmax(0, auto) repeat(5, min-content)";
                extra_toolbar.appendChild(ch_refresh);
            }
        }

        update_card_for_civitai_with_sd1_8();

    } else {
        for (let prefix of tab_prefix_list) {
            let extra_network_refresh_btn = gradioApp().getElementById(prefix+"_extra_refresh");
            if (!extra_network_refresh_btn) continue;

            let ch_refresh = document.createElement("button");
            ch_refresh.innerHTML = "🔁";
            ch_refresh.title = "Refresh Civitai Helper buttons";
            ch_refresh.className = "lg secondary gradio-button";
            ch_refresh.style.fontSize = "200%";
            ch_refresh.onclick = function(){
                update_card_for_civitai();
            };

            extra_network_refresh_btn.parentNode.appendChild(ch_refresh);
        }

        update_card_for_civitai();
    }


    let ch_observer_timer = null;
    const ch_observer = new MutationObserver((mutations) => {
        if (ch_observer_timer) clearTimeout(ch_observer_timer);
        ch_observer_timer = setTimeout(() => {
            if (is_forge_or_new) {
                update_card_for_civitai_with_sd1_8();
            } else {
                update_card_for_civitai();
            }
        }, 500);
    });

    setTimeout(() => {
        for (const tab_prefix of tab_prefix_list) {
            for (const js_model_type of model_type_list) {
                let extra_network_id = tab_prefix + "_" + js_model_type + "_" + cardid_suffix;
                let extra_network_node = gradioApp().getElementById(extra_network_id);
                if (extra_network_node) {
                    ch_observer.observe(extra_network_node, {
                        childList: true,
                        subtree: true
                    });
                }
            }
        }
    }, 1000);


    function ch_inject_extension_manager() {
        let ext_tab = gradioApp().getElementById("tab_extensions");
        if (!ext_tab) return;

        let installed_tab = ext_tab.querySelector("#extensions_installed");
        if (!installed_tab) return;

        if (installed_tab.querySelector(".ch-ext-manager-header")) return;

        let header = document.createElement("div");
        header.className = "ch-ext-manager-header";
        header.style.cssText = "margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 8px;";

        let title = document.createElement("h3");
        title.textContent = "Extension Manager (by Civitai Helper)";
        title.style.cssText = "margin: 0 0 8px 0; font-size: 16px;";
        header.appendChild(title);

        let desc = document.createElement("p");
        desc.textContent = "Uninstall or force-update extensions directly from this page.";
        desc.style.cssText = "margin: 0 0 8px 0; font-size: 13px; color: #aaa;";
        header.appendChild(desc);

        installed_tab.insertBefore(header, installed_tab.firstChild);

        let rows = installed_tab.querySelectorAll("tr");
        for (let row of rows) {
            if (row.querySelector(".ch-ext-uninstall-btn")) continue;

            let name_cell = row.querySelector("td:first-child");
            if (!name_cell) continue;

            let ext_name = name_cell.textContent.trim();
            if (!ext_name) continue;

            let btn_cell = document.createElement("td");
            btn_cell.style.whiteSpace = "nowrap";

            let uninstall_btn = document.createElement("button");
            uninstall_btn.textContent = "🗑 Uninstall";
            uninstall_btn.className = "ch-ext-uninstall-btn";
            uninstall_btn.style.cssText = "padding: 2px 8px; margin-right: 4px; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;";
            uninstall_btn.onclick = function() {
                if (!confirm(`Uninstall extension "${ext_name}"?\nThis will delete the extension folder and cannot be undone.`)) return;
                let msg = {
                    "action": "uninstall_extension",
                    "extension_name": ext_name,
                };
                let js_uninstall_ext_btn = gradioApp().getElementById("ch_js_uninstall_ext_btn");
                if (js_uninstall_ext_btn) {
                    send_ch_py_msg(msg);
                    js_uninstall_ext_btn.click();
                }
            };
            btn_cell.appendChild(uninstall_btn);

            let force_update_btn = document.createElement("button");
            force_update_btn.textContent = "🔄 Force Update";
            force_update_btn.className = "ch-ext-force-update-btn";
            force_update_btn.style.cssText = "padding: 2px 8px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;";
            force_update_btn.onclick = function() {
                if (!confirm(`Force update extension "${ext_name}"?\nThis will run git reset --hard and git pull on the extension.`)) return;
                let msg = {
                    "action": "force_update_extension",
                    "extension_name": ext_name,
                };
                let js_force_update_ext_btn = gradioApp().getElementById("ch_js_force_update_ext_btn");
                if (js_force_update_ext_btn) {
                    send_ch_py_msg(msg);
                    js_force_update_ext_btn.click();
                }
            };
            btn_cell.appendChild(force_update_btn);

            row.appendChild(btn_cell);
        }
    }

    let ch_ext_observer_timer = null;
    const ch_ext_observer = new MutationObserver(() => {
        if (ch_ext_observer_timer) clearTimeout(ch_ext_observer_timer);
        ch_ext_observer_timer = setTimeout(() => {
            ch_inject_extension_manager();
        }, 500);
    });

    setTimeout(() => {
        let ext_tab = gradioApp().getElementById("tab_extensions");
        if (ext_tab) {
            ch_ext_observer.observe(ext_tab, {
                childList: true,
                subtree: true,
            });
            ch_inject_extension_manager();
        }
    }, 2000);

});
