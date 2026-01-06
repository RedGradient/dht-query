- `lookup`: Add an option to stop iff a certain number of total peers are found?
- `lookup`: Implement a "give up" condition so we don't run forever if there
  aren't any peers?
- Add a multi-query node ID lookup command that implements the node lookup
  described by the Kademlia paper
- Add a command for checking whether a given node ID+IP pair is BEP
  42-compliant
    - Give `get-node-id` an `--ip IP` option to make it also check whether our
      node ID is compliant?
- `set-node-id`: Support passing IPv6 addresses to `--ip`
- Add an `announce-peer` command?
- Give single-packet commands a `--json` option for outputting JSON?
    - Represent bytes fields as hexadecimal
    - Represent `InetAddr` values as `HOST:PORT` strings?
- Add an `-x`/`--hex` option for pretty-printing unparsed bytes fields as
  `bytes.fromhex('…')`
- Add an option for setting the UDP port to use?
    - Separate options for IPv4 and IPv6?
- Add options controlling whether to use IPv4 and/or IPv6

- Support BEP 33?
- Support BEP 44 commands?
    - For "put", this would mean letting the user specify a bencoded data
      value.  How should that be supplied?  Read from a given bencoded file?
- Support BEP 50?

- Fill out `--help` text
- Fill out README
- Put on GitHub?
