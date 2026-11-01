#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webserver plugin of WAS, which provides some webserver funkions and a websocket,
which can translate websocket messages into WAS internal events and vice versa

"""

import os
import json
import time
from pprint import pprint

# Non standard modules (install with pip)

from typing import Optional
import webbrowser
import socket
from flask import Flask, send_from_directory
from flask_sockets import Sockets, Rule
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# own local modules

from was.common.jsonstorage import JsonStorage

from was.splthread import SplThread
import was.defaults as defaults


class WebsocketUser:
    """handles all user related data"""

    def __init__(self, name, websocket):
        self.name = name
        self.ws = websocket


class SplPlugin(SplThread):
    """Instance of the base SplThread class"""

    plugin_id = "webserver"
    plugin_names = ["Flask Webserver"]

    def __init__(self, module_reference):
        """creates the HTTP and websocket server"""

        self.modref = module_reference
        self.program_dir = os.path.dirname(__file__)
        super().__init__(module_reference.message_handler, self)
        # reads the config, if any
        self.config = JsonStorage(
            "webserver",
            "backup",
            "config.json",
            {
                "server_config": {
                    "credentials": "",
                    "host": "0.0.0.0",
                    "port": 8000,
                    "secure": False,
                    "openbrowser": True,
                },
                "actual_settings": {
                    "www_root_dir": os.path.realpath(
                        os.path.join(self.program_dir, "../../../static")
                    )
                },
            },
        )
        self.server_config = self.config.read("server_config", {})
        # set up the argument parser with values from the config

        self.app = Flask("webserver")
        self.sockets = Sockets(self.app)
        self.server: Optional[pywsgi.WSGIServer] = None
        self.ws_clients = []  # my actual browser connections
        self.modref.message_handler.add_event_handler(
            "webserver", 0, self.event_listener
        )
        # https://githubmemory.com/repo/heroku-python/flask-sockets/activity
        self.sockets.url_map.add(
            Rule("/ws", endpoint=self.on_create_ws_socket, websocket=True)
        )

        @self.app.route("/")
        def index(path="index.html"):
            root_dir = self.config.read("actual_settings")
            if root_dir is None or "www_root_dir" not in root_dir:
                return "no www_root_dir configured"
            if not os.path.exists(root_dir["www_root_dir"]):
                return "www_root_dir does not exist"
            return send_from_directory(
                os.path.join(root_dir["www_root_dir"], ""),
                path,
            )

    def on_create_ws_socket(self, websocket):
        """distributes incoming messages to the registered event handlers

        Args:
                message (:obj:`str`): json string, representing object with
                'type' as identifier and 'config' containing the data
        """
        user = self.find_user_by_ws(websocket)
        if user:
            if user != websocket:
                self.disconnect()
                user = self.connect(websocket)
        else:
            user = self.connect(websocket)
        while not websocket.closed:
            message = websocket.receive()
            if message:
                # self.log_message('websocket received "%s"', str(message))
                try:
                    data = json.loads(message)
                    if (
                        "type" in data
                        and data["type"] == "_join"
                        and "config" in data
                        and "name" in data["config"]
                    ):  # its a _join message
                        user.name = data["config"]["name"]
                    self.modref.message_handler.queue_event(
                        user.name, defaults.MSG_SOCKET_BROWSER, data
                    )
                except json.decoder.JSONDecodeError as ex:
                    print("message Exception:", str(ex))

    def connect(self, websocket):
        """thows a connect event about that new connection"""
        # self.log_message('%s', 'websocket connected')
        user = WebsocketUser(None, websocket)
        self.ws_clients.append(user)
        self.modref.message_handler.queue_event(
            user.name, defaults.MSG_SOCKET_CONNECT, None
        )
        return user

    def find_user_by_ws(self, websocket):
        """finds the user object by the websocket object"""
        for user in self.ws_clients:
            if user.ws == websocket:
                return user
        return None

    def find_user_by_user_name(self, user_name):
        """finds the user object by the user name"""
        for user in self.ws_clients:
            if user.name == user_name:
                return user
        return None

    def disconnect(self):
        """thows a close event about the closed connection"""
        user = self.find_user_by_user_name(None)
        if user:
            user.ws.close()
            self.ws_clients.remove(user)
            # self.log_message('%s', 'websocket closed')
            self.modref.message_handler.queue_event(
                user.name, defaults.MSG_SOCKET_CLOSE, None
            )

    def emit(self, message_type, config):
        """sends data object as JSON string to websocket client

        Args:
        type (:obj:`str`): string identifier of the contained data type
        config (:obj:`obj`): data object to be sent
        """

        message = {"type": message_type, "config": config}
        user = self.find_user_by_user_name(None)
        if user:
            pprint(message)
            if user.ws:
                if not user.ws.closed:
                    user.ws.send(json.dumps(message))
                else:
                    self.ws_clients.remove(user)

    def event_listener(self, queue_event) -> Optional[dict]:
        """checks all incoming queue_events if to be send to one or all users"""
        # print("webserver event handler",queue_event.type,queue_event.user)
        if queue_event.type == defaults.MSG_SOCKET_MSG:
            message = {
                "type": queue_event.data["type"],
                "config": queue_event.data["config"],
            }
            json_message = json.dumps(message)
            dead_users = []
            for user in self.ws_clients:
                if queue_event.user is None or queue_event.user == user.name:
                    try:
                        user.ws.send(json_message)
                    except socket.error as ex:
                        print("Websocket send error", str(ex))
                        dead_users.append(user)
            for user in dead_users:
                self.ws_clients.remove(user)

            return None  # no futher handling of this event
        return queue_event

    def plugin_run(self):
        """starts the server"""
        try:
            self.server = pywsgi.WSGIServer(
                (self.server_config["host"], self.server_config["port"]),
                self.app,
                handler_class=WebSocketHandler,
            )
            ## read the epa dir with the actual settings

            if self.server_config["secure"]:
                print(
                    f"initialized secure https server at port {self.server_config['port']}"
                )
                webbrowser.open(
                    f"https://{self.find_own_ip()}:{self.server_config['port']}", new=2
                )
            else:
                print(f"initialized http server at port {self.server_config['port']}")
            if self.server_config["openbrowser"]:
                webbrowser.open(
                    f"http://{self.find_own_ip()}:{self.server_config['port']}", new=2
                )

            self.server.serve_forever()

            # os.chdir(origin_dir)
        except KeyboardInterrupt:
            print("^C received, shutting down server")
            if self.server:
                self.server.stop()

    def plugin_stop(self):
        if self.server:
            self.server.stop()

    def query_handler(self, queue_event, max_result_count) -> Optional[list]:
        """handler for system queries"""
        pass

    # https://www.delftstack.com/de/howto/python/get-ip-address-python/
    def find_own_ip(self) -> str:
        """tries to identify the own ip

        Returns:
            str: the ip number
        """

        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = "127.0.0.1"
        try:
            st.connect(("10.255.255.255", 1))
            ip = st.getsockname()[0]
        except socket.error:
            pass
        finally:
            st.close()
        return ip


if __name__ == "__main__":

    class ModRef:
        """Storage object to"""

        store = None
        message_handler = None

    modref = ModRef()
    ws = SplPlugin(modref)
    ws.run()
    while True:
        time.sleep(1)
    ws.stop()
