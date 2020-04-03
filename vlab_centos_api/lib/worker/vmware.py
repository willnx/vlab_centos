# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import random
import os.path
from celery.utils.log import get_task_logger
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_centos_api.lib import const


logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_CENTOS_LOG_LEVEL.upper())


def show_centos(username):
    """Obtain basic information about CentOS

    :Returns: Dictionary

    :param username: The user requesting info about their CentOS
    :type username: String
    """
    centos_vms = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for vm in folder.childEntity:
            info = virtual_machine.get_info(vcenter, vm, username)
            if info['meta']['component'] == 'CentOS':
                centos_vms[vm.name] = info
    return centos_vms


def delete_centos(username, machine_name, logger):
    """Unregister and destroy a user's CentOS

    :Returns: None

    :param username: The user who wants to delete their jumpbox
    :type username: String

    :param machine_name: The name of the VM to delete
    :type machine_name: String

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity, username)
                if info['meta']['component'] == 'CentOS':
                    logger.debug('powering off VM')
                    virtual_machine.power(entity, state='off')
                    delete_task = entity.Destroy_Task()
                    logger.debug('blocking while VM is being destroyed')
                    consume_task(delete_task)
                    break
        else:
            raise ValueError('No {} named {} found'.format('centos', machine_name))


def create_centos(username, machine_name, image, network, desktop, ram, cpu_count, logger):
    """Deploy a new instance of CentOS

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new CentOS
    :type username: String

    :param machine_name: The name of the new instance of CentOS
    :type machine_name: String

    :param image: The image/version of CentOS to create
    :type image: String

    :param network: The name of the network to connect the new CentOS instance up to
    :type network: String

    :param network: The name of the network to connect the new CentOS instance up to
    :type network: String

    :param desktop: Deploy the VM with a GUI
    :type desktop: Boolean

    :param ram: The number of GB of RAM to allocate for the VM
    :type ram: Integer

    :param cpu_count: The number of CPU cores to allocate for the VM
    :type cpu_count: Integer

    :param logger: An object for logging messages
    :type logger: logging.LoggerAdapter
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        image_name = convert_name(image, desktop=desktop)
        logger.info(image_name)
        try:
            ova = Ova(os.path.join(const.VLAB_CENTOS_IMAGES_DIR, image_name))
        except FileNotFoundError:
            error = "Invalid version of CentOS supplied: {}".format(image)
            raise ValueError(error)
        try:
            network_map = vim.OvfManager.NetworkMapping()
            network_map.name = ova.networks[0]
            try:
                network_map.network = vcenter.networks[network]
            except KeyError:
                raise ValueError('No such network named {}'.format(network))
            the_vm = virtual_machine.deploy_from_ova(vcenter, ova, [network_map],
                                                     username, machine_name, logger,
                                                     power_on=False)
        finally:
            ova.close()
        mb_of_ram = ram * 1024
        virtual_machine.adjust_ram(the_vm, mb_of_ram)
        virtual_machine.adjust_cpu(the_vm, cpu_count)
        virtual_machine.power(the_vm, state='on')
        meta_data = {'component' : "CentOS",
                     'created': time.time(),
                     'version': image,
                     'configured': False,
                     'generation': 1,
                    }
        virtual_machine.set_meta(the_vm, meta_data)
        info = virtual_machine.get_info(vcenter, the_vm, username, ensure_ip=True)
        return {the_vm.name: info}

def list_images():
    """Obtain a list of available versions of CentOS that can be created

    :Returns: List
    """
    images = os.listdir(const.VLAB_CENTOS_IMAGES_DIR)
    images = list(set([convert_name(x, to_version=True) for x in images]))
    return images


def convert_name(name, to_version=False, desktop=False):
    """This function centralizes converting between the name of the OVA, and the
    version of software it contains.

    OVA files have the following naming convention: CentOS-<version>.ova, i.e. CentOS-7.ova

    :param name: The thing to covert
    :type name: String

    :param to_version: Set to True to covert the name of an OVA to the version
    :type to_version: Boolean

    :param desktop: Set to True to obtain the name of the OVA that includes a GUI
    :type desktop: Boolean
    """
    if to_version:
        return name.split('-')[-1].replace('.ova', '')
    elif desktop:
        return 'CentOS-desktop-{}.ova'.format(name)
    else:
        return 'CentOS-{}.ova'.format(name)


def update_network(username, machine_name, new_network):
    """Implements the VM network update

    :param username: The name of the user who owns the virtual machine
    :type username: String

    :param machine_name: The name of the virtual machine
    :type machine_name: String

    :param new_network: The name of the new network to connect the VM to
    :type new_network: String
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity, username)
                if info['meta']['component'] == 'CentOS':
                    the_vm = entity
                    break
        else:
            error = 'No VM named {} found'.format(machine_name)
            raise ValueError(error)

        try:
            network = vcenter.networks[new_network]
        except KeyError:
            error = 'No VM named {} found'.format(machine_name)
            raise ValueError(error)
        else:
            virtual_machine.change_network(the_vm, network)
