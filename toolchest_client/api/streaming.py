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
        self.initialized = False

    def initialize_params(self, streaming_token, streaming_ip_address, streaming_tls_cert):
        self.streaming_token = streaming_token
        self.streaming_ip_address = streaming_ip_address
        self.streaming_tls_cert = streaming_tls_cert

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(cadata=self.streaming_tls_cert)
        self.ssl_context = ssl_context

        self.initialized = True

    async def receive_stream(self):
        streaming_username = "toolchest"
        streaming_port = "8765"
        uri = f"wss://{streaming_username}:{self.streaming_token}@{self.streaming_ip_address}:{streaming_port}"
        async with websockets.connect(uri, ssl=self.ssl_context) as websocket:
            stream_is_open = True
            while stream_is_open:
                try:
                    stream_lines = await websocket.recv()
                    print(stream_lines, end="")
                except ConnectionClosed:
                    stream_is_open = False
                    print("==> End of stream, connection closed by server <==")

    def run_receive_stream(self):
        asyncio.run(self.receive_stream())
