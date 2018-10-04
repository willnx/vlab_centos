# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from celery.utils.log import get_task_logger

from vlab_centos_api.lib import const
from vlab_centos_api.lib.worker import vmware

app = Celery('centos', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_CENTOS_LOG_LEVEL.upper())


@app.task(name='centos.show')
def show(username):
    """Obtain basic information about CentOS

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_centos(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='centos.create')
def create(username, machine_name, image, network):
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
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_centos(username, machine_name, image, network)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='centos.delete')
def delete(username, machine_name):
    """Destroy an instance of CentOS

    :Returns: Dictionary

    :param username: The name of the user who wants to delete an instance of CentOS
    :type username: String

    :param machine_name: The name of the instance of CentOS
    :type machine_name: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_centos(username, machine_name)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='centos.image')
def image():
    """Obtain a list of available images/versions of CentOS that can be created

    :Returns: Dictionary
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp