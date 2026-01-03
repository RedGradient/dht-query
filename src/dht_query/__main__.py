from __future__ import annotations
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from pprint import pprint
import random
import socket
from types import TracebackType
from typing import Any
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


def parse_info_hash(s: str) -> bytes:
    bs = bytes.fromhex(s)
    if len(bs) != 20:
        raise ValueError("info hashes must be 20 bytes long")
    return bs


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
        expand_ip(msg)
        pprint(msg)


@main.command()
@click.option("--want4", is_flag=True)
@click.option("--want6", is_flag=True)
@click.argument("addr", type=InetAddr.parse)
@click.argument("infohash", type=parse_info_hash)
def get_peers(addr: InetAddr, infohash: bytes, want4: bool, want6: bool) -> None:
    with UdpSocket().connect(addr) as conn:
        query: dict[bytes, Any] = {
            b"t": gen_transaction_id(),
            b"y": b"q",
            b"q": b"get_peers",
            b"a": {
                b"id": MY_NODE_ID,
                b"info_hash": infohash,
            },
            b"v": b"TEST",
            b"ro": 1,
        }
        if want4 or want6:
            want = []
            if want4:
                want.append(b"n4")
            if want6:
                want.append(b"n6")
            query[b"a"][b"want"] = want
        conn.send(bencode(query))
        reply = conn.recv()
        msg = unbencode(reply)
        expand_ip(msg)
        pprint(msg)


def gen_transaction_id() -> bytes:
    return random.randbytes(TRANSACTION_ID_LEN)


def expand_ip(msg: dict[bytes, Any]) -> None:
    if (addr := msg.get(b"ip")) is not None and isinstance(addr, bytes):
        if len(addr) == 6:
            ip4 = IPv4Address(addr[:4])
            port = int.from_bytes(addr[4:])
            msg[b"ip"] = (ip4, port)
        elif len(addr) == 18:
            ip6 = IPv6Address(addr[:16])
            port = int.from_bytes(addr[16:])
            msg[b"ip"] = (ip6, port)


if __name__ == "__main__":
    main()
