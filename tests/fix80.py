#!/usr/bin/env python3

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

import json
import argparse
import logging

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get accessories app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-o', action='store', dest='output', default='compact', choices=['json', 'compact'],
                        help='Specify output format')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()
    setup_logging(args.loglevel)
    logging.getLogger().setLevel(logging.INFO)

    controller = Controller(args.adapter)
    controller.load_data(args.file)

    pairing = controller.get_pairings()[args.alias]

    # save and remove accessories
    acc = pairing.pairing_data['accessories']
    del pairing.pairing_data['accessories']

    # without accessories in pairing data, this will trigger a load of the accessories and characteristics
    logging.getLogger().setLevel(logging.DEBUG)
    # data = pairing.list_accessories_and_characteristics()

    # restore the accessories data and establish a session by reading a characteristic
    logging.getLogger().setLevel(logging.INFO)
    pairing.pairing_data['accessories'] = acc
    r = pairing.get_characteristics([(1, 4)])

    # remove accessories again and try to load the accessories and characteristics again
    del pairing.pairing_data['accessories']
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug(80 * '-')
    data = pairing.list_accessories_and_characteristics()

    print(json.dumps(data, indent=4))

