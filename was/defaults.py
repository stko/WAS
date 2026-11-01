#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""default values for the WAS framework"""

WEB_ROOT_DIR = "../static"

# all the different message types
MSG_SYSTEM_READY = "systemready"
MSG_SYSTEM_SHUTDOWN = "systemshutdown"
MSG_SOCKET_APP_USER_MESSAGE = "wsappusermessage"  # outgoing message to the Browser
MSG_SOCKET_CONNECT = "wsconnect"
MSG_SOCKET_CLOSE = "wsclose"
MSG_SOCKET_MSG = "wsmsg"  # outgoing message to the Browser
MSG_SOCKET_BROWSER = "wsmsgbrowser"  # incoming message from Browser
MSG_DEBUG_QUERY = "debugquery"  # incoming message from Browser
# feel free to add your own message types here, but please use
# a prefix like "ws" or "wsapp" to avoid conflicts with other plugins
MSG_SOCKET_XXX = "xxxx"

# all the different query types
# feel free to add your own query types here, but please use
# a prefix like "query" or "querywas" to avoid conflicts with other plugins
QUERY_WAS_XXX = "queryxxxx"

# limits the number of search results when do a query
MAX_QUERY_SIZE = 40
