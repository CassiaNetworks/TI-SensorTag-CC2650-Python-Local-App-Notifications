from cassiadevtools.cassia_api import CassiaApi
from collections import defaultdict
import asyncio
import atexit
import asyncio_atexit
from functools import partial

API_DOMAIN_OR_IP_ADDRESS = '192.168.4.25' #'10.10.10.254'

async def scan_connect_notify(api,
                                   scan_filters,
                                   scanned_devices,
                                   connect_options,
                                   connected_devices):
    await api.scan_connect_notify(
        scan_filters,
        scanned_devices,
        connect_options,
        connected_devices,
        ['61', '63'],  # Handles to turn on movement notification and data.
        ['0100', 'ff00'])  # Values to write for movement notification data.

async def notification_stream(api):
    await api.get_notifications()

# TODO: Cover disconnect case when device isn't manually disconnected.
#       Maybe check status of device?
async def exit_handler(api, connected_devices):
    for mac in connected_devices:
        # Turn off notifiactions for movement by writing 0x0000 to handle 61.
        if await api.write(mac, '61','0000'):
            print('Turned OFF movement notification for: ' + mac)
        if await api.disconnect(mac):
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
        scan_connect_notify(
            api,
            scan_filters,
            scanned_devices,
            connect_options,
            connected_devices
        ),
        notification_stream(api),
    )

if __name__ == '__main__':
    asyncio.run(main())
