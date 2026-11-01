#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""main module of the WAS framework"""

import time
import os
from typing import Optional
from was.directorymapper import DirectoryMapper
from was.messagehandler import MessageHandler
import was.waslogger as waslogger
from was.pluginmanager import PluginManager


class ModRef:
    """helper class to store references to the global modules"""

    def __init__(self):
        self.server = None
        self.message_handler: Optional[MessageHandler] = None


def _(s):
    return s


class Was:
    """main class of the WAS framework"""

    def __init__(self, data_volumes_dir: str = __file__):
        self.logger = waslogger.getLogger(__name__)
        self.directory_mapper = DirectoryMapper(
            os.path.abspath(os.path.dirname(data_volumes_dir)),
            {
                "backup": "volumes/backup",
                "runtime": "volumes/runtime",
                "tmpfs": "volumes/tmpfs",
            },
        )
        self.modref = ModRef()  # create object to store all module instances
        self.modref.message_handler = MessageHandler(self.modref)
        self.plugin_manager: Optional[PluginManager] = None

    def run(
        self,
        custom_plugins_dir: Optional[list[str]] = None,
        was_plugins_dir: str = "plugins",
    ):
        """starts the WAS framework"""
        self.plugin_manager = PluginManager(
            self.modref, custom_plugins_dir, was_plugins_dir
        )

        while True:
            time.sleep(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-p", "--plugins", help="directory to load plugins from")

    args = parser.parse_args()
    was = Was()
    was.run(custom_plugins_dir=[args.plugins])
