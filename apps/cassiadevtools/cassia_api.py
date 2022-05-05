"""This module contains a class that interfaces with the Cassia RESTful API.

The CassiaApi class contains methods that interface with the
Cassia RESTful API for the container, router, and AC.

  The api_type parameter

  Typical usage example:

  cassia_api = CassiaApi('container')
  
  cassia_api = CassiaApi('gateway', '192.168.1.48')
  
  cassia_api = CassiaApi('ac', 'demo.cassia.pro')

TODO: Add more Cassia RESTful API methods.
"""

from enum import Enum
from aiohttp_sse_client import client as sse_client
import aiohttp
import asyncio
import json
import time

class CassiaApi:
    CONTAINER_ADDRESS = "10.10.10.254";
    class ApiType(Enum):
        CONTAINER = 'container'
        ROUTER = 'gateway'
        AC = 'ac'

    def __init__(self, api_type, api_domain=CONTAINER_ADDRESS, api_url_protocol='http'):

        self.api_domain = api_domain
        self.api_url_protocol = api_url_protocol
        self.__is_sse_scan = False
        self.__is_sse_notify = False
        self.__ac_access_token = ''

        try:
            self.ApiType(api_type)

        except ValueError as ve:
            print(ve)
            print("Please provide a valid api_type value:"
                  "'container', 'router', 'ac'")
        else:
            self.api_type = self.ApiType(api_type)

        if self.api_type == self.ApiType.AC:
            self.api_domain += '/api'

    async def scan_connect_pair_notify(self, scan_filters=[], scanned_devices={}, connect_options={}, connected_devices={}):
        is_successful = True
        sse_url = ''.join([
            self.api_url_protocol + '://',
            self.api_domain,
            '/gap/nodes?event=1',
        ])

        if len(scan_filters):
            sse_url = sse_url + '&' + '&'.join(scan_filters)

        try:
            async with sse_client.EventSource(sse_url) as event_source:
                async for event in event_source:
                    data = json.loads(event.data)
                    device_mac = data['bdaddrs'][0]['bdaddr']
                    scanned_devices[device_mac] = time.time()

                    # Connect the device.
                    if await self.connect(device_mac, connect_options):
                        connected_devices[device_mac] = 1

                    marked_for_del_macs = []
                    for key, time_val in scanned_devices.items():
                        print(key)
                        if time.time() - time_val >= 30:
                            marked_for_del_macs.append(key)

                    for mac in marked_for_del_macs:
                        del scanned_devices[mac]
        except ConnectionError as e:
            sse_client.resp.close()
            is_successful = False
            raise e
        return is_successful

    async def scan(self, filters, scanned_devices={}):
        is_successful = True
        sse_url = ''.join([
            self.api_url_protocol + '://',
            self.api_domain,
            '/gap/nodes?event=1',
        ])

        if len(filters):
            sse_url = sse_url + '&' + '&'.join(filters)

        try:
            async with sse_client.EventSource(sse_url) as event_source:
                async for event in event_source:
                    data = json.loads(event.data)
                    scanned_devices[data['bdaddrs'][0]['bdaddr']] = time.time()
                    marked_for_del_macs = []
                    for key, time_val in scanned_devices.items():
                        print(key)
                        if time.time() - time_val >= 30:
                            marked_for_del_macs.append(key)

                    for mac in marked_for_del_macs:
                        del scanned_devices[mac]

        except ConnectionError as e:
            sse_client.resp.close()
            is_successful = False
            raise e
        return is_successful

    async def connect(self, device_mac='', options={}):
        is_successful = True
        url = ''.join([
            self.api_url_protocol,
            '://',
            self.api_domain,
            '/gap/nodes/' + device_mac + '/connection',
        ])
        print('connect')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=options) as response:
                  data = await response.text()
                  print (data)
        except aiohttp.ClientError as e:
            is_successful = False
            raise e

        await session.close()
        return is_successful

    async def pair(self, devices):
        is_successful = True
        print('pair')
        return is_successful

    async def unpair(self, devices):
        is_successful = True
        print('unpair')
        return is_successful

    async def disconnect(self, device_mac):
        is_successful = True
        url = ''.join([
            self.api_url_protocol + '://',
            self.api_domain,
            '/gap/nodes/' + device_mac + '/connection'
        ])
        print('disconnect')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url) as response:
                  data = await response.text()
                  print (data)
        except aiohttp.ClientError as e:
            is_successful = False
            raise e

        await session.close()
        return is_successful

    async def write(self, handle, value):
        is_successful = True
        url = ''.join([
            self.api_url_protocol + '://',
            self.api_domain,
            '/gatt/nodes/' + device_mac,
            '/handle/' + handle,
            '/value/' + value, # '/handle/61/value/0100'
        ])
        print('writing value ' + value + 'to handle ' + handle + '.')
        return is_successful
