#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from _socket import inet_ntoa
from time import sleep

from zeroconf import Zeroconf, ServiceBrowser

from homekit.model import Categories
from homekit.model.feature_flags import FeatureFlags


class CollectingListener(object):
    def __init__(self):
        self.data = []

    def remove_service(self, zeroconf, type, name):
        # this is ignored since not interested in disappearing stuff
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info is not None:
            self.data.append(info)

    def get_data(self):
        return self.data


def discover_homekit_devices(max_seconds=10):
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(max_seconds)
    tmp = []
    for info in listener.get_data():
        # from Bonjour discovery
        d = {
            'name': info.name,
            'address': inet_ntoa(info.address),
            'port': info.port
        }

        # stuff taken from the Bonjour TXT record (see table 5-7 on page 69)

        if b'c#' not in info.properties:
            continue
        d['c#'] = info.properties[b'c#'].decode()

        if b'ff' not in info.properties:
            flags = 0
        else:
            flags = int(info.properties[b'ff'].decode())
        d['ff'] = flags
        d['flags'] = FeatureFlags[flags]

        if b'id' not in info.properties:
            continue
        d['id'] = info.properties[b'id'].decode()

        if b'md' not in info.properties:
            continue
        d['md'] = info.properties[b'md'].decode()

        if b'pv' in info.properties:
            d['pv'] = info.properties[b'pv'].decode()
        else:
            d['pv'] = '1.0'

        if b's#' not in info.properties:
            continue
        d['s#'] = info.properties[b's#'].decode()

        if b'sf' not in info.properties:
            d['sf'] = 0
        else:
            d['sf'] = info.properties[b'sf'].decode()

        if b'ci' not in info.properties:
            continue
        category = info.properties[b'ci'].decode()
        d['ci'] = category
        d['category'] = Categories[int(category)]

        # append device, it has all data
        tmp.append(d)

    zeroconf.close()
    return tmp


def find_device_ip_and_port(device_id: str, max_seconds=10):
    """
    Try to find a HomeKit Accessory via Bonjour. The process is time boxed by the second parameter which sets an upper
    limit of `max_seconds` before it times out. The runtime of the function may be longer because of the Bonjour handling
    code.

    :param device_id: the Accessory's pairing id
    :param max_seconds: the number of seconds to wait for the accessory to be found
    :return: a dict with ip and port if the accessory was found or None
    """
    result = None
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    counter = 0

    while result is None and counter < max_seconds:
        sleep(1)
        data = listener.get_data()
        for info in data:
            if info.properties[b'id'].decode() == device_id:
                result = {'ip': inet_ntoa(info.address), 'port': info.port}
                break
        counter += 1

    zeroconf.close()
    return result
