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

import argparse
import sys, traceback, json
from homekit.controller import Controller
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.services import ServicesTypes

ACCESSORY_UNDER_TEST = 'accessoryUnderTest'


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit initialize storage')
    parser.add_argument('-d', action='store', required=False, dest='deviceId')
    parser.add_argument('-p', action='store', required=False, dest='devicePin')
    return parser.parse_args()


def print_device(info, file=None):
    print('Name: {name}'.format(name=info['name']), file=file)
    print('Url: http_impl://{ip}:{port}'.format(ip=info['address'], port=info['port']), file=file)
    print('Configuration number (c#): {conf}'.format(conf=info['c#']), file=file)
    print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=info['flags'], flags=info['ff']), file=file)
    print('Device ID (id): {id}'.format(id=info['id']), file=file)
    print('Model Name (md): {md}'.format(md=info['md']), file=file)
    print('Protocol Version (pv): {pv}'.format(pv=info['pv']), file=file)
    print('State Number (s#): {sn}'.format(sn=info['s#']), file=file)
    print('Status Flags (sf): {sf}'.format(sf=info['sf']), file=file)
    print('Category Identifier (ci): {c} (Id: {ci})'.format(c=info['category'], ci=info['ci']), file=file)
    print(file=file)


def show_status(text, file=None):
    print(text)
    if file:
        print(text, file=file)
        file.flush()


if __name__ == '__main__':
    args = setup_args_parser()

    with open('testresult', 'w') as reportfile:

        controller = Controller()
        results = controller.discover()
        valid_device_ids = {}
        for info in results:
            valid_device_ids[info['id']] = info
            print_device(info)

        selected_device_id = ''
        if args.deviceId:
            selected_device_id = args.deviceId
        while selected_device_id not in valid_device_ids:
            selected_device_id = input('Enter device id (or -1 to quit): ')
            if selected_device_id == '-1':
                sys.exit(-1)

        show_status('continuing with device \'{id}\'.'.format(id=selected_device_id), file=reportfile)
        print_device(valid_device_ids[selected_device_id], file=reportfile)

        #
        #   try to identify unpaired accessory
        #
        show_status('\ntrying to identify unpaired...', file=reportfile)
        try:
            controller.identify(selected_device_id)
            show_status('identify unpaired worked fine', file=reportfile)
        except Exception as e:
            show_status('error while identify unpaired', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)
            sys.exit(-1)

        #
        #   try to pair accessory
        #
        show_status('\ntrying to pair', file=reportfile)
        if args.devicePin:
            pairing_pin = args.devicePin
        else:
            pairing_pin = input('Enter pairing pin: ')
        try:
            controller.perform_pairing(ACCESSORY_UNDER_TEST, selected_device_id, pairing_pin)
            pairing = controller.get_pairings()[ACCESSORY_UNDER_TEST]
            controller.save_data('testpairingdata')
            show_status('pairing worked fine', file=reportfile)
        except Exception as e:
            show_status('error while pairing', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)
            sys.exit(-1)

        #
        #   try to identify paired
        #
        show_status('\ntrying to identify paired...', file=reportfile)
        try:
            pairing.identify()
            show_status('identify paired worked fine', file=reportfile)
        except Exception as e:
            show_status('error while identify paired', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)

        #
        #   try to read accessories and characteristics
        #
        show_status('\ntrying to list accessories and characteristics...', file=reportfile)
        try:
            accessories_and_characteristics = pairing.list_accessories_and_characteristics()
            controller.save_data('testpairingdata')
#            show_status(json.dumps(accessories_and_characteristics, indent=4), file=reportfile)
            for accessory in accessories_and_characteristics:
                aid = accessory['aid']
                for service in accessory['services']:
                    s_type = service['type']
                    s_iid = service['iid']
                    show_status('{aid}.{iid}: >{stype}<'.format(aid=aid, iid=s_iid, stype=ServicesTypes.get_short(s_type)), file=reportfile)

                    for characteristic in service['characteristics']:
                        c_iid = characteristic['iid']
                        value = characteristic.get('value', '')
                        c_type = characteristic['type']
                        perms = ','.join(characteristic['perms'])
                        desc = characteristic.get('description', '')
                        c_type = CharacteristicsTypes.get_short(c_type)
                        show_status('  {aid}.{iid}: {value} ({description}) >{ctype}< [{perms}]'.format(aid=aid,
                                                                                                  iid=c_iid,
                                                                                                  value=value,
                                                                                                  ctype=c_type,
                                                                                                  perms=perms,
                                                                                                  description=desc), file=reportfile)
            show_status('list accessories and characteristics worked fine', file=reportfile)
        except Exception as e:
            show_status('error while list accessories and characteristics', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)

        #
        #   try to read single characteristic
        #
        show_status('\ntrying to read characteristic...', file=reportfile)
        try:
            aid = accessories_and_characteristics[0]['aid']
            iid = accessories_and_characteristics[0]['services'][0]['characteristics'][0]['iid']
            result = pairing.get_characteristics([(aid, iid)], include_meta=True, include_perms=True, include_type=True,
                                                 include_events=True)
            show_status(str(result), file=reportfile)
            show_status('read characteristic worked fine', file=reportfile)
        except Exception as e:
            show_status('error while read characteristic', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)

        #
        #   try to read multiple characteristics
        #
        show_status('\ntrying to read multiple characteristics...', file=reportfile)
        try:
            aid = accessories_and_characteristics[0]['aid']
            iid = accessories_and_characteristics[0]['services'][0]['characteristics'][0]['iid']
            iid2 = accessories_and_characteristics[0]['services'][0]['characteristics'][1]['iid']
            result = pairing.get_characteristics([(aid, iid), (aid, iid2)], include_meta=True, include_perms=True,
                                                 include_type=True, include_events=True)
            show_status(str(result), file=reportfile)
            show_status('read multiple characteristics worked fine', file=reportfile)
        except Exception as e:
            show_status('error while multiple characteristics', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)

        #
        #   try to unpair
        #
        show_status('\ntrying to unpair', file=reportfile)
        try:
            controller.remove_pairing(ACCESSORY_UNDER_TEST)
            show_status('unpairing worked fine', file=reportfile)
        except Exception as e:
            show_status('error while identify paired', file=reportfile)
            show_status(e, file=reportfile)
            traceback.print_exc(file=reportfile)
