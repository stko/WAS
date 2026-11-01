"""Base class for implementing threaded plugins."""

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import threading
from abc import ABCMeta, abstractmethod
from typing import Optional

# Non standard modules (install with pip)


# own local modules

import was.defaults as defaults


class SplThread(metaclass=ABCMeta):
    """Partly abstract class to implement threading & message handling"""

    def __init__(self, msg_handler, child):
        self.msg_handler = msg_handler
        self.child = child
        self.th: Optional[threading.Thread] = None

    @abstractmethod
    def plugin_run(self):
        """starts the thread loop"""

    @abstractmethod
    def plugin_stop(self):
        """stops the thread loop"""

    @abstractmethod
    def event_listener(self, queue_event) -> Optional[dict]:
        """handler for system events"""

    @abstractmethod
    def query_handler(self, queue_event, max_result_count) -> Optional[list]:
        """handler for system queries"""

    def run(self):
        """starts the child thread"""
        # Create a Thread with a function without any arguments
        # th = threading.Thread(target=_ws_main, args=(server,))
        self.th = threading.Thread(target=self.child.plugin_run)
        # Start the thread
        self.th.daemon = True
        self.th.start()

    def stop(self, timeout=0):
        """stops the child thread. If timeout > 0, it will wait timeout
        secs for the thread to finish"""
        # https://stackoverflow.com/a/36499538/1927807 how to stop a thread in python
        self.child.run_flag = False
        self.child.plugin_stop()
        if timeout > 0 and self.th is not None:
            self.th.join(timeout)
            return self.th.is_alive()

    def user_message(self, user, user_message, user_button_text="OK"):
        """sends a user message to the browser. The user_message is a
        string, the user_button_text is optional and defaults to "OK".
        The user_message will be displayed in a popup window in the
        browser, and the user_button_text will be displayed on the
        button to close the popup window. The user parameter is
        the name of the user to send the message to. If user is None,
        the message will be sent to all users.
        """
        self.msg_handler.queue_event(
            user,
            defaults.MSG_SOCKET_MSG,
            {
                "type": defaults.MSG_SOCKET_APP_USER_MESSAGE,
                "config": {
                    "user_message": user_message,
                    "user_button_text": user_button_text,
                },
            },
        )
