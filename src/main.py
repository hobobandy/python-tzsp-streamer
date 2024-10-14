import argparse
import os

from loguru import logger

from .utils.CaptureInterface import CaptureInterface
from .utils.CaptureStreamer import CaptureStreamer


def main():
    parser = argparse.ArgumentParser(description='Remote Packet Capture Agent')
    parser.add_argument('--interface', type=str, required=True, help='Interface to capture on')
    parser.add_argument('--dstip', type=str, required=True, help='IP to forward traffic to')
    parser.add_argument('--dstport', type=int, required=False, default=37008, help='Port to forward traffic to')
    parser.add_argument('--packetfilter', type=str, required=False, help='Packet filter in libpcap filter syntax')

    args = parser.parse_args()

    # Let's make sure we're running as root
    # We do this after the initial argparse to allow --help calls as non-root
    if not (os.geteuid() == 0):
        logger.error("this script must run as root to sniff interfaces; please use sudo")
    else:
      # Prepare parameters
      interface = str(args.interface)
      dstip = str(args.dstip)
      dstport = int(args.dstport)
      packet_filter = ['not port ' + str(dstport)] # Filter out ourselves
      if args.packetfilter:
        packet_filter.insert(0, str(args.packetfilter))

      # Prepare the interface we'll sniff on
      i = CaptureInterface(interface)

      # Let's make sure device is in monitor mode
      if i.get_mode() == 'monitor':
        logger.info("Interface '%s' is already in monitor mode, good!" % i.dev)
      else:
        logger.info("Attempting to put interface '%s' in monitor mode..." % i.dev)
        i.enable_monitor_mode()
        logger.info("Interface '%s' should now be in monitor mode." % i.dev)
      
      # Start the streamer
      s = CaptureStreamer(interface)
      s.start(dstip, dstport, " and ".join(packet_filter))
