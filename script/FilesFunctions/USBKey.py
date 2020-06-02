#!/usr/bin/env python3


import pyudev
import psutil


class USBKey():
    def __init__(self):
        self.usbPath = self.findUSBPath()

    def findUSBPath(self):
        context = pyudev.Context()
        removable = [device for device in context.list_devices(
            subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
        for device in removable:
            partitions = [device.device_node for device in context.list_devices(
                subsystem='block', DEVTYPE='partition', parent=device)]

            for p in psutil.disk_partitions():
                if p.device in partitions:
                    return p.mountpoint
        return False

    def getPath(self):
        return self.usbPath


if __name__ == '__main__':
    try:
        usb = USBKey()
        print(usb.getPath())
    except:
        pass
