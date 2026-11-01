"""Sample plugin for the myAppName application. This plugin is a
template for creating new plugins. It is not intended to be used
as is, but rather as a starting point for creating new plugins.
The plugin is a subclass of the SplThread class, which is a base
class for all plugins. The SplThread class provides a thread that
runs in the background and can be used to perform tasks that need
to run in the background, such as monitoring a directory for new
files or processing data in the background.

The SplThread class also provides methods for sending messages to
the user interface and for handling events and queries from the user
interface.

The SplPlugin class is a subclass of the SplThread class and provides
a template for creating new plugins.

The SplPlugin class provides methods for handling events and queries
from the user interface, as well as methods for starting and stopping
the plugin. The SplPlugin class also provides a method for performing
tasks in the background, which can be overridden by subclasses to
perform specific tasks."""

#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
import time
import threading

# Non standard modules (install with pip)


# own local modules
from was import defaults
from was.splthread import SplThread
from was.common.jsonstorage import JsonStorage


class SplPlugin(SplThread):
    """Instance of the base SplThread class"""

    plugin_id = "myplugin"
    plugin_names = ["My Plugin Name"]

    def __init__(self, modref):
        """inits the plugin"""
        self.modref = modref

        # do the plugin specific initialisation first

        self.movielist_storage = JsonStorage(
            self.plugin_id, "runtime", "myplugin.json", {"movielist": {}}
        )  # set defaults

        self.lock = threading.Lock()  # create a lock, only if necessary

        # at last announce the own plugin
        super().__init__(modref.message_handler, self)
        modref.message_handler.add_event_handler(self.plugin_id, 0, self.event_listener)
        modref.message_handler.add_query_handler(self.plugin_id, 0, self.query_handler)
        self.run_flag = True

    def event_listener(self, queue_event):
        """try to send simulated answers"""
        # print("uihandler event handler", queue_event.type, queue_event.user)
        if queue_event.type == defaults.MSG_SOCKET_XXX:
            pass
        if queue_event.type == "_join":
            print("a web client has connected", queue_event.data)
        # for further pocessing, do not forget to return the queue event
        return queue_event

    def query_handler(self, queue_event, max_result_count):
        # print("myplugin handler query handler",
        # queue_event.type,  queue_event.user, max_result_count)
        if queue_event.type == defaults.MSG_SOCKET_XXX:  # wait for defined messages
            pass
        return []

    def plugin_run(self):
        """starts the server"""
        # https://stackoverflow.com/a/36499538/1927807
        t = threading.current_thread()
        while getattr(t, "run_flag", True):
            time.sleep(10)
            with self.lock:
                pass

    def plugin_stop(self):
        self.run_flag = False

    # ------ plugin specific routines
