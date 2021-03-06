# -*- coding: UTF-8 -*-
"""
Defines the RESTful API for the CentOS service
"""
import ujson
from flask import current_app
from flask_classy import request, route, Response
from vlab_inf_common.views import MachineView
from vlab_inf_common.vmware import vCenter, vim
from vlab_api_common import describe, get_logger, requires, validate_input


from vlab_centos_api.lib import const


logger = get_logger(__name__, loglevel=const.VLAB_CENTOS_LOG_LEVEL)


class CentOSView(MachineView):
    """API end point for working with CentOS VMs"""
    route_base = '/api/2/inf/centos'
    RESROUCE = 'centos'
    POST_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "description": "Create a centos",
                    "properties": {
                        "name": {
                            "description": "The name to give your CentOS instance",
                            "type": "string"
                        },
                        "image": {
                            "description": "The image/version of CentOS to create",
                            "type": "string"
                        },
                        "network": {
                            "description": "The network to hook the CentOS instance up to",
                            "type": "string"
                        },
                        "desktop": {
                            "description": "Deploy the VM with a GUI",
                            "type": "boolean",
                            "default": "false",
                        },
                        "cpu-count": {
                            "description": "The number of CPU cores to allocate to the VM",
                            "type": "integer",
                            "default": 4,
                            "enum": [4, 8, 12]
                        },
                        "ram": {
                            "description": "The number of GB of RAM to allocate to the VM",
                            "type": "integer",
                            "default": 4,
                            "enum": [4, 6, 8]
                        }
                    },
                    "required": ["name", "image", "network"]
                  }
    DELETE_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "Destroy a CentOS",
                     "type": "object",
                     "properties": {
                        "name": {
                            "description": "The name of the CentOS instance to destroy",
                            "type": "string"
                        }
                     },
                     "required": ["name"]
                    }
    GET_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                  "description": "Display the CentOS instances you own"
                 }
    IMAGES_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "View available versions of CentOS that can be created"
                    }


    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @describe(post=POST_SCHEMA, delete=DELETE_SCHEMA, get=GET_SCHEMA)
    def get(self, *args, **kwargs):
        """Display the CentOS instances you own"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        task = current_app.celery_app.send_task('centos.show', [username, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @validate_input(schema=POST_SCHEMA)
    def post(self, *args, **kwargs):
        """Create a CentOS"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        body = kwargs['body']
        machine_name = body['name']
        image = body['image']
        desktop = body.get('desktop', False)
        ram = body.get('ram', 4)
        cpu_count = body.get('cpu-count', 4)
        network = '{}_{}'.format(username, body['network'])
        task = current_app.celery_app.send_task('centos.create', [username,
                                                                  machine_name,
                                                                  image,
                                                                  network,
                                                                  desktop,
                                                                  ram,
                                                                  cpu_count,
                                                                  txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @validate_input(schema=DELETE_SCHEMA)
    def delete(self, *args, **kwargs):
        """Destroy a CentOS"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        machine_name = kwargs['body']['name']
        task = current_app.celery_app.send_task('centos.delete', [username, machine_name, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @route('/image', methods=["GET"])
    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @describe(get=IMAGES_SCHEMA)
    def image(self, *args, **kwargs):
        """Show available versions of CentOS that can be deployed"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        task = current_app.celery_app.send_task('centos.image', [txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp
