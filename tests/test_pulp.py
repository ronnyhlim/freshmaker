# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

import json

from unittest.mock import patch
from requests import exceptions

from freshmaker.pulp import Pulp
from freshmaker import conf
from tests import helpers


class TestPulp(helpers.FreshmakerTestCase):
    """Test interface to Pulp"""

    def setUp(self):
        super(TestPulp, self).setUp()
        self.server_url = 'http://localhost/'
        self.username = 'qa'
        self.password = 'qa'

    @patch('freshmaker.pulp.requests.post')
    def test_query_content_set_by_repo_ids(self, post):
        post.return_value.json.return_value = [
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-workstation-rpms__7Workstation__x86_64/',
                '_id':
                {
                    '$oid': '53853a247bc9f61b85909cfe'
                },
                'id': 'rhel-7-workstation-rpms__7Workstation__x86_64',
                'notes':
                {
                    'content_set': 'rhel-7-workstation-rpms',
                },
            },
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-hpc-node-rpms__7ComputeNode__x86_64/',
                '_id': {
                    '$oid': '5384ee7c7bc9f619942a8f89',
                },
                'id': 'rhel-7-hpc-node-rpms__7ComputeNode__x86_64',
                'notes': {
                    'content_set': 'rhel-7-hpc-node-rpms'
                },
            },
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-desktop-rpms__7Client__x86_64/',
                '_id': {
                    '$oid': '5384ee6a7bc9f619942a8bca',
                },
                'id': 'rhel-7-desktop-rpms__7Client__x86_64',
                'notes': {
                    'content_set': 'rhel-7-desktop-rpms',
                }
            }
        ]

        pulp = Pulp(self.server_url, username=self.username, password=self.password)
        repo_ids = [
            'rhel-7-hpc-node-rpms__7ComputeNode__x86_64',
            'rhel-7-workstation-rpms__7Workstation__x86_64',
            'rhel-7-desktop-rpms__7Client__x86_64',
        ]
        content_sets = pulp.get_content_set_by_repo_ids(repo_ids)

        post.assert_called_once_with(
            '{}pulp/api/v2/repositories/search/'.format(self.server_url),
            json.dumps({
                'criteria': {
                    'filters': {
                        'id': {'$in': repo_ids},
                    },
                    'fields': ['notes'],
                }
            }),
            auth=(self.username, self.password),
            timeout=conf.requests_timeout)

        self.assertEqual(
            ['rhel-7-workstation-rpms',
             'rhel-7-hpc-node-rpms',
             'rhel-7-desktop-rpms'],
            content_sets)

    @patch('freshmaker.pulp.requests.post')
    def test_get_content_sets_by_ignoring_nonexisting_ones(self, post):
        post.return_value.json.return_value = [
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-workstation-rpms__7Workstation__x86_64/',
                '_id':
                {
                    '$oid': '53853a247bc9f61b85909cfe'
                },
                'id': 'rhel-7-workstation-rpms__7Workstation__x86_64',
                'notes':
                {
                    'content_set': 'rhel-7-workstation-rpms',
                },
            },
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-hpc-node-rpms__7ComputeNode__x86_64/',
                '_id': {
                    '$oid': '5384ee7c7bc9f619942a8f89',
                },
                'id': 'rhel-7-hpc-node-rpms__7ComputeNode__x86_64',
                'notes': {},
            },
            {
                '_href': '/pulp/api/v2/repositories/rhel-7-desktop-rpms__7Client__x86_64/',
                '_id': {
                    '$oid': '5384ee6a7bc9f619942a8bca',
                },
                'id': 'rhel-7-desktop-rpms__7Client__x86_64',
                'notes': {
                    'content_set': 'rhel-7-desktop-rpms',
                }
            }
        ]

        pulp = Pulp(self.server_url, username=self.username, password=self.password)
        repo_ids = [
            'rhel-7-hpc-node-rpms__7ComputeNode__x86_64',
            'rhel-7-workstation-rpms__7Workstation__x86_64',
            'rhel-7-desktop-rpms__7Client__x86_64',
        ]
        content_sets = pulp.get_content_set_by_repo_ids(repo_ids)

        post.assert_called_once_with(
            '{}pulp/api/v2/repositories/search/'.format(self.server_url),
            json.dumps({
                'criteria': {
                    'filters': {
                        'id': {'$in': repo_ids},
                    },
                    'fields': ['notes'],
                }
            }),
            auth=(self.username, self.password),
            timeout=conf.requests_timeout)

        self.assertEqual(['rhel-7-workstation-rpms', 'rhel-7-desktop-rpms'],
                         content_sets)

    @patch('freshmaker.pulp.requests.get')
    def test_get_docker_repository_name(self, get):
        get.return_value.json.return_value = {
            'display_name': 'foo-526',
            'description': 'Foo',
            'distributors': [
                {'repo_id': 'foo-526',
                 'distributor_type_id': 'docker_distributor_web',
                 'config': {'repo-registry-id': 'scl/foo-526'}}
            ]
        }

        pulp = Pulp(self.server_url, username=self.username, password=self.password)
        repo_name = pulp.get_docker_repository_name("foo-526")

        get.assert_called_once_with(
            '{}pulp/api/v2/repositories/foo-526/'.format(self.server_url),
            params={"distributors": True},
            auth=(self.username, self.password),
            timeout=conf.requests_timeout)

        self.assertEqual(repo_name, "scl/foo-526")

    @patch('freshmaker.pulp.requests.post')
    @patch('freshmaker.pulp.requests.get')
    def test_retrying_calls(self, get, post):
        get.side_effect = exceptions.HTTPError("Connection error: get")
        post.side_effect = exceptions.HTTPError("Connection error: post")

        pulp = Pulp(self.server_url, username=self.username,
                    password=self.password)

        with self.assertRaises(exceptions.HTTPError):
            pulp.get_docker_repository_name("test")
        self.assertGreater(get.call_count, 1)

        with self.assertRaises(exceptions.HTTPError):
            pulp.get_content_set_by_repo_ids(['test1', 'test2'])
        self.assertGreater(post.call_count, 1)
