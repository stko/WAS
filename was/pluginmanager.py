#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""search for the plugins, loads them and start them all
depending on the pluginmanager config file"""

# Standard module
import sys
import os
import importlib
import importlib.util
import traceback
import re
from typing import Optional

# Non standard modules (install with pip)

# own local modules
from was.common.jsonstorage import JsonStorage
import was.defaults as defaults


class PluginManager:
    """loads all was plugins"""

    def __init__(
        self,
        modref,
        custom_plugins_dir: Optional[list[str]] = None,
        was_plugins_dir: str = "",
    ):
        self.origin_dir = os.path.dirname(__file__)
        if not was_plugins_dir:
            was_plugins_dir = os.path.realpath(os.path.join(self.origin_dir, "plugins"))
        self.config = JsonStorage(
            "PluginManager", "backup", "plugins.json", {"plugins": {}}
        )
        self.plugins = {}
        regex = re.compile(r"^spl_.+.py$")
        custom_plugins_dir = custom_plugins_dir or []
        # remove empty strings from the list
        custom_plugins_dir = [d for d in custom_plugins_dir if d]
        custom_plugins_dir.append(was_plugins_dir)
        custom_plugins_dir = [
            os.path.realpath(os.path.join(self.origin_dir, d))
            for d in custom_plugins_dir
        ]
        try:
            new_plugins_found = False
            config_plugins = self.config.read("plugins", {})
            for plugin_path in custom_plugins_dir:
                list_subfolders_with_paths = [
                    f.path for f in os.scandir(plugin_path) if f.is_dir()
                ]
                for sub_folder in list_subfolders_with_paths:
                    list_file_infos = [f for f in os.scandir(sub_folder) if f.is_file()]
                    for file_info in list_file_infos:
                        if regex.match(file_info.name):
                            print(file_info.path)

                            module_spec = importlib.util.spec_from_file_location(
                                file_info.name, file_info.path
                            )
                            if module_spec is None:
                                print(
                                    "Can't load plugin "
                                    + file_info.name
                                    + " from "
                                    + file_info.path
                                )
                                continue
                            my_module = importlib.util.module_from_spec(module_spec)
                            if module_spec.loader is None:
                                print(
                                    "Can't load plugin "
                                    + file_info.name
                                    + " from "
                                    + file_info.path
                                )
                                continue
                            module_spec.loader.exec_module(my_module)
                            plugin_id = my_module.SplPlugin.plugin_id
                            if not plugin_id in config_plugins:  # new module
                                config_plugins[plugin_id] = {"active": True}
                                new_plugins_found = True
                                continue
                            if not config_plugins[plugin_id]["active"]:
                                continue

                            instance = my_module.SplPlugin(modref)
                            self.plugins[file_info.name] = instance
            if new_plugins_found:
                self.config.write("plugins", config_plugins)
            # finally run all active modules
            for instance in self.plugins.values():
                instance.run()
            modref.message_handler.queue_event(
                None,
                defaults.MSG_SYSTEM_READY,
                None,
            )
        except Exception as e:
            print("Can't load plugin " + str(e))
            traceback.print_exc(file=sys.stdout)
