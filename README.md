# python-tzsp-streamer

Stream 802.11 frames encapsulated in [TaZmen Sniffer Protocol (TZSP)](https://en.wikipedia.org/wiki/TZSP) over UDP to a remote host.

## Requirements

### Python

* [PyShark](https://github.com/KimiNewt/pyshark) (therefore tshark)
* [Loguru](https://github.com/Delgan/loguru)

### System

* [iw](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html)

## Wireshark

Tested with Wireshark Version 4.4.1, it should work with older versions with the TZSP dissector.

### Configuration

* Make sure the destination port matches the TZSP port configured in `Edit > Preferences > Protocols > TZSP`.
* Make sure TZSP is enabled under `Analyze > Enabled Protocols`.

1. Start a capture on the network interface with the destination IP.
2. Use the display filter `tzsp` to only show streamed frames.

### Known Quirks

* Columns with dynamic fields (Source, Destination, etc.) will show local IP, or other matching fields, therefore it may be useful to create a custom [Configuration Profile](https://www.wireshark.org/docs/wsug_html_chunked/ChCustConfigProfilesSection.html) in Wireshark with more specific columns (e.g., `wlan.sa` field for Source).

## Roadmap

* Stream Ethernet packets (add a CLI switch)
* Improve CLI output to include statistics
* Include a service file and process mode

## Credit

Initial code idea came from [Nick vs Networking](https://nickvsnetworking.com/)'s [Scratch'n'Sniff](https://github.com/nickvsnetworking/Scratch-n-Sniff) project.
