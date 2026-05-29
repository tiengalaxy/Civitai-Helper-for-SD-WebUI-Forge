# -*- coding: UTF-8 -*-
import json
from . import util

js_actions = ("open_url", "add_trigger_words", "use_preview_prompt", "dl_model_new_version", "remove_card", "apply_lora_with_strength", "save_note", "get_trigger_words", "get_model_file_size", "batch_get_model_data", "uninstall_extension", "force_update_extension")
py_actions = ("open_url", "remove_card", "get_trigger_words", "get_model_file_size", "batch_get_model_data", "uninstall_extension", "force_update_extension")


def parse_js_msg(msg):
    util.printD("Start parse js msg")
    util.printD(f"Msg: {msg}")

    try:
        msg_dict = json.loads(msg)
    except (json.JSONDecodeError, TypeError) as e:
        util.printD(f"Failed to parse js msg as JSON: {str(e)}")
        return None

    if type(msg_dict) == str:
        try:
            msg_dict = json.loads(msg_dict)
        except (json.JSONDecodeError, TypeError) as e:
            util.printD(f"Failed to parse nested js msg as JSON: {str(e)}")
            return None

    if "action" not in msg_dict.keys():
        util.printD("Can not find action from js request")
        return None

    action = msg_dict["action"]
    if not action:
        util.printD("Action from js request is None")
        return None

    if action not in js_actions:
        util.printD("Unknow action: " + action)
        return None

    util.printD("End parse js msg")

    return msg_dict


def build_py_msg(action:str, content:dict):
    util.printD("Start build_msg")
    if not content:
        util.printD("Content is None")
        return ""

    if not action:
        util.printD("Action is None")
        return ""

    if action not in py_actions:
        util.printD("Unknow action: " + action)
        return ""

    msg = {
        "action" : action,
        "content": content
    }

    util.printD("End build_msg")
    return json.dumps(msg)
