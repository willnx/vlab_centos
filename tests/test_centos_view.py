# -*- coding: UTF-8 -*-
"""
A suite of tests for the centos object
"""
import unittest
from unittest.mock import patch, MagicMock

import ujson
from flask import Flask
from vlab_api_common import flask_common
from vlab_api_common.http_auth import generate_v2_test_token


from vlab_centos_api.lib.views import centos


class TestCentOSView(unittest.TestCase):
    """A set of test cases for the CentOSView object"""
    @classmethod
    def setUpClass(cls):
        """Runs once for the whole test suite"""
        cls.token = generate_v2_test_token(username='bob')

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        centos.CentOSView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        # Mock Celery
        app.celery_app = MagicMock()
        cls.fake_task = MagicMock()
        cls.fake_task.id = 'asdf-asdf-asdf'
        app.celery_app.send_task.return_value = cls.fake_task

    def test_v1_deprecated(self):
        """CentOSView - GET on /api/1/inf/centos returns an HTTP 404"""
        resp = self.app.get('/api/1/inf/centos',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 404

        self.assertEqual(status, expected)

    def test_get_task(self):
        """CentOSView - GET on /api/2/inf/centos returns a task-id"""
        resp = self.app.get('/api/2/inf/centos',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_get_task_link(self):
        """CentOSView - GET on /api/2/inf/centos sets the Link header"""
        resp = self.app.get('/api/2/inf/centos',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/centos/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_post_task(self):
        """CentOSView - POST on /api/2/inf/centos returns a task-id"""
        resp = self.app.post('/api/2/inf/centos',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myCentOSBox",
                                   'image': "someVersion"})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_post_task_link(self):
        """CentOSView - POST on /api/2/inf/centos sets the Link header"""
        resp = self.app.post('/api/2/inf/centos',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myCentOSBox",
                                   'image': "someVersion"})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/centos/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_delete_task(self):
        """CentOSView - DELETE on /api/2/inf/centos returns a task-id"""
        resp = self.app.delete('/api/2/inf/centos',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myCentOSBox'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_delete_task_link(self):
        """CentOSView - DELETE on /api/2/inf/centos sets the Link header"""
        resp = self.app.delete('/api/2/inf/centos',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myCentOSBox'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/centos/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """CentOSView - GET on the ./image end point returns the a task-id"""
        resp = self.app.get('/api/2/inf/centos/image',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """CentOSView - GET on the ./image end point returns the a task-id"""
        resp = self.app.get('/api/2/inf/centos/image',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/centos/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)


if __name__ == '__main__':
    unittest.main()
