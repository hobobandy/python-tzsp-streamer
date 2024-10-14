import pyshark
import signal
import socket
import threading

from loguru import logger


class CaptureStreamer:
    def __init__(self, interface):
        self._stopped_event = threading.Event() # Event used for clean exit
        self._thread = None
        self.interface = interface
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
    
    def should_keep_running(self):
        """Determines whether the thread should continue running."""
        return not self._stopped_event.is_set()
    
    def handle_signal(self, signum, frame):
        logger.warning(f"Received {signal.Signals(signum).name}")
        self.stop()
    
    def start(self, dstip, dstport, packet_filter):
        self._thread = threading.Thread(target=self.run, args=(dstip, dstport, packet_filter))
        logger.info("Starting streamer.")
        self._thread.start()
    
    def stop(self):
        logger.info(f"Stopping streamer, this may take a few seconds.")
        self._stopped_event.set()
        if self._thread is threading.Thread:
            return self._thread.join()
    
    def run(self, dstip, dstport, packet_filter):
        capture = pyshark.LiveCapture(interface=self.interface, include_raw=True, use_json=True, bpf_filter=packet_filter)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        logger.info("Sniffing - Press Ctrl-C to exit.")
        for packet in capture.sniff_continuously():
            if self.should_keep_running():
                # TZSP Header for IEEE 802.11 with RadioTap header
                # https://github.com/wireshark/wireshark/blob/master/epan/dissectors/packet-tzsp.c
                data = packet.get_raw_packet()
                data = '0100007E01' + data.hex()
                sock.sendto(bytes.fromhex(data), (dstip, dstport))
            else:
                logger.info("Sniffing stopped.")
                break
