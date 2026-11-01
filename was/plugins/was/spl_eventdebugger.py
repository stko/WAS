#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""a developing helper which allows to view and inject internal events and queries"""

# Standard module
import time
import threading

# Non standard modules (install with pip)

# own local modules
from was.messagehandler import Query
from was import defaults
from was.splthread import SplThread
from was.common.jsonstorage import JsonStorage


class SplPlugin(SplThread):
    """Instance of the base SplThread class"""

    plugin_id = "eventdebugger"
    plugin_names = ["Websocket Event Debugger"]

    def __init__(self, modref):
        """inits the plugin"""
        self.modref = modref

        # do the plugin specific initialisation first

        self.movielist_storage = JsonStorage(
            self.plugin_id, "backup", "eventdebugger.json", {"settings": {}}
        )  # set defaults

        self.lock = threading.Lock()  # create a lock, only if necessary
        self.debugger_connected = False
        self.debugger_name = "wasdebugger"
        # at last announce the own plugin
        super().__init__(modref.message_handler, self)
        modref.message_handler.add_event_handler(self.plugin_id, 0, self.event_listener)
        modref.message_handler.add_query_handler(self.plugin_id, 0, self.query_handler)

    def event_listener(self, queue_event):
        """handle incoming events"""
        # print("uihandler event handler", queue_event.type, queue_event.user)
        if (
            queue_event.type == defaults.MSG_SOCKET_BROWSER
        ):  # the websocket has got a query from the websocket
            if "wasdebug" in queue_event.data:
                debug_msg = queue_event.data["wasdebug"]
                if "query" in debug_msg and "event" in debug_msg:
                    event = debug_msg["event"]
                    if debug_msg["query"]:
                        unlimited = True
                        if "unlimited" in debug_msg:
                            unlimited = debug_msg["unlimited"]
                        query = Query(
                            event["name"], event["type"], event["config"], unlimited
                        )
                        res = self.modref.message_handler.query(query)
                        self.modref.message_handler.queue_event(
                            self.debugger_name,
                            defaults.MSG_SOCKET_MSG,
                            {"type": defaults.MSG_DEBUG_QUERY, "config": res},
                        )
                    else:
                        self.modref.message_handler.queue_event(
                            event["name"], event["type"], event["config"]
                        )
            if "type" in queue_event.data and queue_event.data["type"] == "_join":
                print("a web client has connected", queue_event.data)
                if (
                    "name" in queue_event.data["config"]
                    and queue_event.data["config"]["name"] == self.debugger_name
                ):
                    self.debugger_connected = True
        # send all events to the debugger, if connected
        if self.debugger_connected:
            self.modref.message_handler.queue_event(
                self.debugger_name,
                defaults.MSG_SOCKET_MSG,
                {"type": queue_event.type, "config": queue_event.data},
            )

        # for further pocessing, do not forget to return the queue event
        return queue_event

    def query_handler(self, queue_event, max_result_count):
        if queue_event.type == defaults.MSG_SOCKET_XXX:  # no own queries
            # print("eventdebugger handler query handler",
            # queue_event.type,  queue_event.user, max_result_count)
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
        t = threading.current_thread()
        setattr(t, "run_flag", False)

    # ------ plugin specific routines
