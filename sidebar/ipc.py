import json
import os
import socket
from typing import Self

import jq


class _UmbrielIPCClient:
    """Client for interacting with Umbriel IPC via Unix domain socket."""

    def __init__(self, timeout: float = 5.0) -> None:
        self.socket_path = os.environ["UMBRIEL_SOCKET"]
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self._buffer = bytearray()

    def connect(self) -> None:
        """Establishes a connection to the Unix domain socket."""
        if self.sock is not None:
            self.close()

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)
        self._buffer.clear()

    def send_cmd(self, cmd: str) -> str:
        """
        Sends a string command to the socket and reads the response until a newline character '\\n'.

        Returns the response string without the trailing '\\n' (and without '\\r' if it was present).
        """
        if self.sock is None:
            raise RuntimeError("Socket is not connected. Call connect() first.")

        # Ensure the command is sent as bytes
        self.sock.sendall(cmd.encode("utf-8"))

        # Read in chunks until a newline character '\n' appears in the buffer
        while b"\n" not in self._buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                # If the server closed the connection before sending '\n'
                if self._buffer:
                    response = self._buffer.decode("utf-8", errors="replace")
                    self._buffer.clear()
                    return response
                raise ConnectionResetError("The server closed the connection before sending '\\n'.")
            self._buffer.extend(chunk)

        # Extract data up to the first '\n', keep the rest in the buffer
        newline_idx = self._buffer.index(b"\n")
        raw_line = bytes(self._buffer[:newline_idx])
        del self._buffer[: newline_idx + 1]

        return raw_line.decode("utf-8")

    def close(self) -> None:
        """Close the connection."""
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self.sock.close()
                self.sock = None
        self._buffer.clear()

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def umbriel_send_command(cmd: str, jq_query: str | None = None) -> dict | None:
    with _UmbrielIPCClient() as client:
        response = json.loads(client.send_cmd(json.dumps({"cmd": cmd}) + "\n"))
        if "ok" in response:
            response = response["ok"]
            if jq_query:
                response = jq.compile(jq_query).input(response).first()
            return response
        return None

def umbriel_send_action(action: str) -> bool:
    with _UmbrielIPCClient() as client:
        data = json.loads(client.send_cmd(json.dumps({"cmd": "msg", "arg": action}) + "\n"))
        if "ok" in data:
            return True
        if "err" in data:
            print(f"Error: {data['err']}, Action: {action}")
        return False
