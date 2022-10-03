"""
toolchest_client.api.streaming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a StreamingClient object, used by Toolchest queries to
receive and print output lines streamed from the Toolchest server.
"""
import asyncio
import ssl

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
        self.username = "toolchest"
        self.params_initialized = False

    def initialize_params(self, streaming_token, streaming_ip_address, streaming_tls_cert):
        self.streaming_token = streaming_token
        self.streaming_ip_address = streaming_ip_address
        self.streaming_tls_cert = streaming_tls_cert

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cadata=self.streaming_tls_cert)
        self.ssl_context = ssl_context

        self.params_initialized = True

    async def receive_stream(self):
        uri = f"wss://{self.username}:{self.streaming_token}@{self.streaming_ip_address}:8765"
        async with websockets.connect(uri, ssl=self.ssl_context) as websocket:
            stream_is_open = True
            while stream_is_open:
                try:
                    stream_lines = await websocket.recv()
                    print(stream_lines)
                except ConnectionClosed:
                    stream_is_open = False

    def run_receive_stream(self):
        asyncio.run(self.receive_stream())
