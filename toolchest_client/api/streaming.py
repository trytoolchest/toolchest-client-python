"""
toolchest_client.api.streaming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a StreamingClient object, used by Toolchest queries to
receive and print output lines streamed from the Toolchest server.
"""
import asyncio
import signal
import ssl
import time

import websockets
from websockets.exceptions import ConnectionClosed


class StreamingClient:
    """A Toolchest output stream client.

    Provides an interface to output lines streamed from the server.

    """

    def __init__(self):
        self.ssl_context = None
        self.streaming_token = None
        self.streaming_ip_address = None
        self.streaming_tls_cert = None
        self.initialized = False
        self.ready_to_start = False
        self.stream_is_open = False

    def initialize_params(self, streaming_token, streaming_ip_address, streaming_tls_cert):
        self.streaming_token = streaming_token
        self.streaming_ip_address = streaming_ip_address
        self.streaming_tls_cert = streaming_tls_cert

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cadata=self.streaming_tls_cert)
        self.ssl_context = ssl_context
        self.ready_to_start = True
        self.initialized = True

    async def receive_stream(self):
        streaming_username = "toolchest"
        streaming_port = "8765"
        uri = f"wss://{streaming_username}:{self.streaming_token}@{self.streaming_ip_address}:{streaming_port}"
        print("Connecting to remote server for streaming...")
        retry_count = 0
        while True:
            try:
                async for websocket in websockets.connect(uri, ssl=self.ssl_context):
                    try:
                        print("Connected!")
                        self.stream_is_open = True
                        while self.stream_is_open:
                            print("Waiting for next stream...")
                            stream_lines = await websocket.recv()
                            print(stream_lines, end="")
                    except ConnectionClosed:
                        self.stream_is_open = False
                        print("\nConnection closed by server.")
                        return
            except ConnectionRefusedError:
                print("Connection refused error")
                if retry_count > 10:
                    raise RuntimeError("Can't connect to server. Try disabling output streaming and re-running.")
                else:
                    continue

    def done_streaming(self, task):
        print("Done streaming", task.done())
        if task.exception():
            raise task.exception()

    def stream(self):
        print("Setting up streaming")
        self.ready_to_start = False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Jupyter notebooks already have as running event loop, so we need to use that async event loop
            task = loop.create_task(self.receive_stream())
            task.add_done_callback(self.done_streaming)
        else:
            task = asyncio.run(self.receive_stream())

        # Cancel the task (and thus the entire run) on ctrl-c
        loop.add_signal_handler(signal.SIGINT, task.cancel)
