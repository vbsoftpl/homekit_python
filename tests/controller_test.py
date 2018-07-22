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
import tempfile
import threading
import time

from homekit import Controller
from homekit import AccessoryServer
from homekit.model import Accessory
from homekit.model.services import LightBulbService


class T(threading.Thread):
    def __init__(self, accessoryServer):
        threading.Thread.__init__(self)
        self.a_s = accessoryServer

    def run(self):
        self.a_s.publish_device()
        self.a_s.serve_forever()


class TestController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #print('set up class\n')
        cls.config_file = tempfile.NamedTemporaryFile()
        cls.config_file.write("""{
              "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
              "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
              "accessory_pairing_id": "12:34:56:00:01:0A",
              "accessory_pin": "010-22-020",
              "c#": 0,
              "category": "Lightbulb",
              "host_ip": "127.0.0.1",
              "host_port": 54321,
              "name": "unittestLight",
              "peers": {
              },
              "unsuccessful_tries": 0
            }""".encode())
        cls.config_file.flush()

        cls.httpd = AccessoryServer(cls.config_file.name, None)
        accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
        cls.httpd.add_accessory(accessory)
        t = T(cls.httpd)
        t.start()
        time.sleep(10)
        #print('...')
        cls.controller_file = tempfile.NamedTemporaryFile()

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.controller_file = tempfile.NamedTemporaryFile()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.unpublish_device()
        cls.httpd.shutdown()
        cls.config_file.close()
        #print('foo')

    def setUp(self):
        self.controller = Controller()
    #     print('set up \n')

    # def tearDown(self):
    #     print('tear down\n')

    def test_01_discover(self):
        result = self.controller.discover()
        found = False
        for device in result:
            if '12:34:56:00:01:0A' == device['id']:
                found = True
        self.assertTrue(found)

    def test_02_pair(self):
        self.controller.perform_pairing('alias', '12:34:56:00:01:0A', '010-22-020')
        pairings = self.controller.get_pairings()
        self.controller.save_data(TestController.controller_file.name)
        self.assertIn('alias', pairings)

    def test_03_get_accessories(self):
        self.controller.load_data(TestController.controller_file.name)
        result = self.controller.get_pairings()['alias'].get_accessories()
        #print(result)

    def test_04_get_characteristics(self):
        self.controller.load_data(TestController.controller_file.name)
        result = self.controller.get_pairings()['alias'].get_characteristics([(1,4)])
        self.assertIn((1,4), result)
        self.assertIn('value', result[(1,4)])
        self.assertEquals('lusiardi.de',result[(1,4)]['value'])
