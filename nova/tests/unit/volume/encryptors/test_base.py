# Copyright (c) 2013 The Johns Hopkins University/Applied Physics Laboratory
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from nova import keymgr
from nova import test
from nova.tests.unit.keymgr import fake
from nova.volume import encryptors
from nova.volume.encryptors import cryptsetup
from nova.volume.encryptors import luks
from nova.volume.encryptors import nop


class VolumeEncryptorTestCase(test.TestCase):
    def _create(self, device_path):
        pass

    def setUp(self):
        super(VolumeEncryptorTestCase, self).setUp()

        self.stubs.Set(keymgr, 'API', fake.fake_api)

        self.connection_info = {
            "data": {
                "device_path": "/dev/disk/by-path/"
                    "ip-192.0.2.0:3260-iscsi-iqn.2010-10.org.openstack"
                    ":volume-fake_uuid-lun-1",
            },
        }
        self.encryptor = self._create(self.connection_info)

    def test_get_encryptors(self):
        encryption = {'control_location': 'front-end',
                      'provider': 'LuksEncryptor'}
        encryptor = encryptors.get_volume_encryptor(self.connection_info,
                                                    **encryption)
        self.assertIsInstance(encryptor,
                              luks.LuksEncryptor,
                              "encryptor is not an instance of LuksEncryptor")

        encryption = {'control_location': 'front-end',
                      'provider': 'CryptsetupEncryptor'}
        encryptor = encryptors.get_volume_encryptor(self.connection_info,
                                                    **encryption)
        self.assertIsInstance(encryptor,
                              cryptsetup.CryptsetupEncryptor,
                              "encryptor is not an instance of"
                              "CryptsetupEncryptor")

        encryption = {'control_location': 'front-end',
                      'provider': 'NoOpEncryptor'}
        encryptor = encryptors.get_volume_encryptor(self.connection_info,
                                                    **encryption)
        self.assertIsInstance(encryptor,
                              nop.NoOpEncryptor,
                              "encryptor is not an instance of NoOpEncryptor")

    def test_get_error_encryptos(self):
        encryption = {'control_location': 'front-end',
                      'provider': 'ErrorEncryptor'}
        self.assertRaises(ValueError, encryptors.get_volume_encryptor,
                          self.connection_info, **encryption)

    @mock.patch('nova.volume.encryptors.LOG')
    def test_error_log(self, log):
        encryption = {'control_location': 'front-end',
                      'provider': 'TestEncryptor'}
        provider = 'TestEncryptor'
        try:
            encryptors.get_volume_encryptor(self.connection_info, **encryption)
        except Exception as e:
            log.error.assert_called_once_with("Error instantiating "
                                              "%(provider)s: "
                                              "%(exception)s",
                                              {'provider': provider,
                                               'exception': e})
