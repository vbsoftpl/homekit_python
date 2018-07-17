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

import unittest
from zeroconf import Zeroconf, ServiceInfo
import socket


from homekit.zeroconf_impl import find_device_ip_and_port


class TestZeroconf(unittest.TestCase):

    def test_find_without_device(self):
        result = find_device_ip_and_port('00:00:00:00:00:00', 1)
        self.assertIsNone(result)

    def test_find_with_device(self):
        zeroconf = Zeroconf()
        desc = {'id': '00:00:01:00:00:02'}
        info = ServiceInfo('_hap._tcp.local.', 'foo._hap._tcp.local.', address=socket.inet_aton('127.0.0.1'),
                           port=1234, properties=desc, weight=0, priority=0)
        zeroconf.unregister_all_services()
        zeroconf.register_service(info, allow_name_change=True)

        result = find_device_ip_and_port('00:00:01:00:00:02', 10)

        zeroconf.unregister_all_services()

        self.assertIsNotNone(result)
