# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_centos_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_show_gateway(self, fake_vCenter, fake_consume_task, fake_get_info):
        """``centos`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'myCentOS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component': 'CentOS',
                                                'created': 1234,
                                                'version': '7',
                                                'configured': False,
                                                'generation': 1}}

        output = vmware.show_centos(username='alice')
        expected = {'myCentOS': {'meta' : {'component': 'CentOS',
                                           'created': 1234,
                                           'version': '7',
                                           'configured': False,
                                           'generation': 1}}}

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_centos(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_centos`` returns None when everything works as expected"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'CentOSBox'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component': 'CentOS',
                                                'created': 1234,
                                                'version': '7',
                                                'configured': False,
                                                'generation': 1}}

        output = vmware.delete_centos(username='bob', machine_name='CentOSBox', logger=fake_logger)
        expected = None

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_delete_centos_value_error(self, fake_vCenter, fake_consume_task, fake_power, fake_get_info):
        """``delete_centos`` raises ValueError when unable to find requested vm for deletion"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'win10'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'note' : 'CentOS=1.0.0'}

        with self.assertRaises(ValueError):
            vmware.delete_centos(username='bob', machine_name='myOtherCentOSBox', logger=fake_logger)

    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_centos(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_set_meta):
        """``create_centos`` returns a dictionary upon success"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = "CentOSBox"
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        output = vmware.create_centos(username='alice',
                                       machine_name='CentOSBox',
                                       image='1.0.0',
                                       network='someLAN',
                                       logger=fake_logger)
        expected = {'CentOSBox' : {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_centos_invalid_network(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova):
        """``create_centos`` raises ValueError if supplied with a non-existing network"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.return_value.networks = ['someLAN']
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        with self.assertRaises(ValueError):
            vmware.create_centos(username='alice',
                                  machine_name='CentOSBox',
                                  image='1.0.0',
                                  network='someOtherLAN',
                                  logger=fake_logger)

    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_create_centos_bad_image(self, fake_vCenter, fake_consume_task, fake_deploy_from_ova, fake_get_info, fake_Ova):
        """``create_centos`` raises ValueError if supplied with a non-existing image/version of CentOS to deploy"""
        fake_logger = MagicMock()
        fake_get_info.return_value = {'worked': True}
        fake_Ova.side_effect = FileNotFoundError('testing')
        fake_vCenter.return_value.__enter__.return_value.networks = {'someLAN' : vmware.vim.Network(moId='1')}

        with self.assertRaises(ValueError):
            vmware.create_centos(username='alice',
                                  machine_name='CentOSBox',
                                  image='1.0.0',
                                  network='someOtherLAN',
                                  logger=fake_logger)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` - Returns a list of available CentOS versions that can be deployed"""
        fake_listdir.return_value = ['CentOS-6.ova', 'CentOS-7.ova']

        output = vmware.list_images()
        expected = ['6', '7']

        # set() avoids ordering issue in test
        self.assertEqual(set(output), set(expected))

    def test_convert_name(self):
        """``convert_name`` - defaults to converting to the OVA file name"""
        output = vmware.convert_name(name='7')
        expected = 'CentOS-7.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` - can take a OVA file name, and extract the version from it"""
        output = vmware.convert_name('', to_version=True)
        expected = ''

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Returns None upon success"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myCentOS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'CentOS'}}

        result = vmware.update_network(username='pat',
                                       machine_name='myCentOS',
                                       new_network='wootTown')

        self.assertTrue(result is None)

    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network_no_vm(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Raises ValueError if the supplied VM doesn't exist"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myCentOS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'CentOS'}}

        with self.assertRaises(ValueError):
            vmware.update_network(username='pat',
                                  machine_name='SomeOtherMachine',
                                  new_network='wootTown')

    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network_no_network(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Raises ValueError if the supplied new network doesn't exist"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myCentOS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'CentOS'}}

        with self.assertRaises(ValueError):
            vmware.update_network(username='pat',
                                  machine_name='myCentOS',
                                  new_network='dohNet')


if __name__ == '__main__':
    unittest.main()
