import re
import subprocess

from loguru import logger


class CaptureInterface:
  """ 
  Provides basic functions to interact with capture interfaces
  This class should be driver-agnostic and should be inherited to customize for specific cards
  """

  def __init__(self, iface):
    # Save capture interface's device and physical name
    self.dev = iface
    self.phy = self.get_phy()
    
    # Discover channel capabilities
    self.channels = self.get_channels()
  
  def get_info(self):
    try:
      process = subprocess.run(['iw','dev',self.dev,'info'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except subprocess.CalledProcessError as e:
      if e.returncode == 237:
        logger.critical(f"Device ({self.dev}) does not exist")
      else:
        logger.critical(f"Unexpected error while getting device's info: {e}")
    else:
      return process
  
  def get_addr(self):
    info = self.get_info()
    addr = re.search(r'addr ([a-fA-F0-9:]+)\n', info.stdout)
    if not addr:
      logger.critical(f"Couldn't find device's mac address using command: {' '.join(info.args)}")
    elif len(addr.groups()) > 1: # failsafe, shouldn't happen
      logger.critical(f"Unexpected number of mac address (addr) listed using command: {' '.join(info.args)}")
      return False
    else:
      return "phy%s" % addr.group(1)

  def get_phy(self):
    info = self.get_info()
    wiphy = re.search(r'wiphy ([0-9]+)\n', info.stdout)
    if not wiphy:
      logger.critical(f"Couldn't find device's physical name using command: {' '.join(info.args)}")
      return False
    elif len(wiphy.groups()) > 1: # failsafe, shouldn't happen
      logger.critical(f"Unexpected number of physical names (wiphy) listed using command: {' '.join(info.args)}")
      return False
    else:
      return "phy%s" % wiphy.group(1)

  def get_mode(self):
    info = self.get_info()
    mode = re.search(r'type ([a-z]+)\n', info.stdout)
    if not mode:
      logger.critical(f"Couldn't find device's mode using command: {' '.join(info.args)}")
    elif len(mode.groups()) > 1: # failsafe, shouldn't happen
      logger.critical(f"Unexpected number of device modes listed using command: {' '.join(info.args)}")
      return False
    else:
      return mode.group(1)
  
  def get_channels(self):
    try:
      process = subprocess.run(['iw','phy',self.phy,'channels'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except subprocess.CalledProcessError as e:
      logger.critical(f"Unexpected error while reading device's supported channels: {e}")
      return False
    else:
      return re.findall(r'MHz \[([0-9]{1,3})\]', process.stdout)
  
  def enable_monitor_mode(self):
    try:
      subprocess.run(['ip','link','set',self.dev,'down'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
      subprocess.run(['iw',self.dev,'set','monitor','control'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
      subprocess.run(['ip','link','set',self.dev,'up'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except subprocess.CalledProcessError as e:
      logger.critical(f"Unexpected error while switching device to monitor mode: {e}")
      return False
    else:
      return True
  
  def change_channel(self, channel):
    try:
      subprocess.run(['iw',self.dev,'set','channel',channel], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except subprocess.CalledProcessError as e:
      logger.critical(f"Unexpected error while changing device's channel: {e}")
      return False
    else:
      return True
