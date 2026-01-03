from __future__ import annotations
from dataclasses import dataclass
from pprint import pprint
import random
import socket
from types import TracebackType
import click
from .bencode import bencode, unbencode

MY_NODE_ID = bytes.fromhex("e2bbceb25a531beca0489e46fd2a68b084363c09")

UDP_PACKET_LEN = 65535

TRANSACTION_ID_LEN = 2

TIMEOUT = 60


@dataclass
class InetAddr:
    host: str
    port: int

    @classmethod
    def parse(cls, s: str) -> InetAddr:
        host, colon, port_str = s.partition(":")
        if not colon:
            raise ValueError(f"invalid address: {s!r}")
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"invalid address: {s!r}")
        return cls(host=host, port=port)


@dataclass
class UdpSocket:
    s: socket.SocketType

    def __init__(self) -> None:
        self.s = socket.socket(type=socket.SOCK_DGRAM)
        self.s.settimeout(TIMEOUT)
        self.s.bind(("0.0.0.0", 0))

    def connect(self, addr: InetAddr) -> UdpConnection:
        self.s.connect((addr.host, addr.port))
        return UdpConnection(self)


@dataclass
class UdpConnection:
    socket: UdpSocket

    def __enter__(self) -> UdpConnection:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        self.socket.s.close()

    def send(self, msg: bytes) -> None:
        self.socket.s.send(msg)

    def recv(self) -> bytes:
        return self.socket.s.recv(UDP_PACKET_LEN)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Query the DHT"""
    pass


@main.command()
@click.argument("addr", type=InetAddr.parse)
def ping(addr: InetAddr) -> None:
    with UdpSocket().connect(addr) as conn:
        query = {
            b"t": gen_transaction_id(),
            b"y": b"q",
            b"q": b"ping",
            b"a": {b"id": MY_NODE_ID},
            b"v": b"TEST",
            b"ro": 1,
        }
        conn.send(bencode(query))
        reply = conn.recv()
        msg = unbencode(reply)
        pprint(msg)


def gen_transaction_id() -> bytes:
    return random.randbytes(TRANSACTION_ID_LEN)


if __name__ == "__main__":
    main()
