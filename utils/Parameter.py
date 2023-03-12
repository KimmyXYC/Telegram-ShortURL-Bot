# -*- coding: utf-8 -*-
# @Time： 2023/3/12 11:32 
# @FileName: Parameter.py
# @Software： PyCharm
# @GitHub: KimmyXYC
import json
import pathlib


def get_config_file():
    with open((str(pathlib.Path.cwd()) + "/Config/Config.json"), 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        json_file.close()
    return data


def get_parameter(*parameters):
    config = get_config_file()
    value = config
    try:
        for parameter in parameters:
            value = value.get(str(parameter))
    except AttributeError:
        value = config["default"]
    return value


def save_config(value, user):
    with open((str(pathlib.Path.cwd()) + "/Config/Config.json"), 'r+', encoding='utf-8') as json_file:
        data = json.load(json_file)
        if user in data["user"]:
            data["user"][user]["URL"] = value
        else:
            data["user"][user] = {"URL": f"{value}"}
        json_file.seek(0)
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        json_file.truncate()
        json_file.close()


def save_default_config(value):
    with open((str(pathlib.Path.cwd()) + "/Config/Config.json"), 'r+', encoding='utf-8') as json_file:
        data = json.load(json_file)
        data["default"] = value
        json_file.seek(0)
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        json_file.truncate()
        json_file.close()
