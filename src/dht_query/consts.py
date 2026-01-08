UDP_PACKET_LEN = 65535

TRANSACTION_ID_LEN = 2

DEFAULT_TIMEOUT = 15.0

CLIENT = b"TEST"

IPV4_REGEX = r"\d+\.\d+\.\d+\.\d+"

# Allow periods in order to support "mixed" addresses in which the last 32 bits
# are in IPv4 format, like ":ffff:192.0.2.128"
IPV6_REGEX = r"[A-Fa-f0-9:.]+"
