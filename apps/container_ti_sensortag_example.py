from cassiadevtools.cassia_api import CassiaApi
from collections import defaultdict
import asyncio
import atexit
import asyncio_atexit
from functools import partial

API_DOMAIN_OR_IP_ADDRESS = '192.168.4.25'  #'10.10.10.254'

async def scan_connect_pair_notify(api,
                                   scan_filters,
                                   scanned_devices,
                                   connect_options,
                                   connected_devices):
    await api.scan_connect_pair_notify(scan_filters, scanned_devices, connect_options, connected_devices)

"""async def connect_devices(api, options, scanned_devices, connected_devices,
                          connected_devices_lock, scanned_devices_lock):
    async with scanned_devices_lock:
        for scanned_dev_mac in scanned_devices:
                # Use the device MAC address to connect.
                is_successful = await api.connect(scanned_dev_mac, options)
                if is_successful:
                    print('connected: ' + scanned_dev_mac)
                    async with connected_devices:
                        connected_devices[scanned_dev_mac] = 1

async def pair_devices(api, connected_devices, paired_devices,
                       paired_devices_lock, connected_devices_lock):
    async with connected_devices_lock:
        for connected_dev_mac in connected_devices.items():
            is_successful = await api.pair(connected_dev_mac)
            if is_successful:
                async with paired_device_lock:
                    paired_devices[connected_dev_mac] = 1  # Set to paired.
"""

# TODO: Cover disconnect case when device isn't manually disconnected.
#       Maybe check status of device?
async def exit_handler(api, connected_devices):
    for mac in connected_devices:
        is_successful = await api.disconnect(mac)
        if is_successful:
            connected_devices[mac] = 0
            print('Disconnected: ' + mac)
        else:
            print('Could not disconnect: ' + mac)

async def main():
    api = CassiaApi('container', API_DOMAIN_OR_IP_ADDRESS)
    
    #scanned_devices_lock = asyncio.Lock()
    connected_devices_lock = asyncio.Lock()
    paired_devices_lock = asyncio.Lock()

    scanned_devices = {}
    connected_devices = {}  # value 0 for not connected, 1 for connected.
    paired_devices = {} # value 0 for unpaired, 1 for paired.
    
    # The active=1 filter allows the Scan API to show the "CC2650 SensorTag"
    # name in scan results. Using the filter_name filter, we can just match the
    # first part of the name using the pattern "CC2650*".
    scan_filters = ['active=1', 'filter_rssi=-70', 'filter_name=CC2650*']

    connect_options = {'timeout': '10000','type': 'public'}

    # Disconnect all devices before ending the program.
    exit_disconnect = partial(exit_handler, api, connected_devices)
    exit_disconnect.__doc__ = 'Disconnects devices upon program exit.'
    asyncio_atexit.register(exit_disconnect)

    await asyncio.gather(
        scan_connect_pair_notify(
            api,
            scan_filters,
            scanned_devices,
            connect_options,
            connected_devices
        ),
        #connect_devices(api, connect_options, scanned_devices, connected_devices,
        #                connected_devices_lock, scanned_devices_lock),
        #pair_devices(api, connected_devices, paired_devices,
        #             paired_devices_lock, connected_devices_lock)
    )

if __name__ == '__main__':
    asyncio.run(main())
