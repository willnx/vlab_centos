#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
centos RESTful API
"""
from setuptools import setup, find_packages


setup(name="vlab-centos-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2020.04.03',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_centos_api' : ['app.ini']},
      description="centos",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery']
      )
