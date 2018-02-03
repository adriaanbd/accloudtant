#   Copyright 2015-2016 See CONTRIBUTORS.md file
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import warnings
import pytest
import accloudtant.aws.prices


class MockEC2Instance(object):
    def __init__(self, instance):
        self.instance = instance

    def __eq__(self, obj):
        if isinstance(obj, dict):
            return self.id == obj['id']
        else:
            return self.id == obj.id

    def console_output(self):
        return self.instance['console_output']

    @property
    def id(self):
        return self.instance['id']

    @property
    def tags(self):
        return self.instance['tags']

    @property
    def instance_type(self):
        return self.instance['instance_type']

    @property
    def placement(self):
        return self.instance['placement']

    @property
    def state(self):
        return self.instance['state']

    @property
    def launch_time(self):
        return self.instance['launch_time']


@pytest.fixture(scope="session")
def ec2_resource():
    class MockEC2Instances(object):
        def __init__(self, instances):
            self.instances = instances

        def all(self):
            for instance in self.instances:
                yield MockEC2Instance(instance)

        def filter(self, Filters=None):
            if Filters is None:
                self.all()
            if Filters[0]['Name'] == 'instance-state-name':
                for instance in self.instances:
                    if instance['state']['Name'] in Filters[0]['Values']:
                        yield MockEC2Instance(instance)

    class MockEC2Resource(object):
        def __init__(self, responses):
            self.responses = responses

        def __getattr__(self, name):
            return MockEC2Instances(self.responses['instances'])

    class MockEC2ResourceCall(object):
        def set_responses(self, responses=None):
            if responses is None:
                responses = {}
            self.responses = responses

        def __call__(self, *args):
            return MockEC2Resource(self.responses)

    return MockEC2ResourceCall()


@pytest.fixture(scope="session")
def ec2_client():
    class MockEC2Client(object):
        def __init__(self, instances, reserved):
            self.instances = instances
            self.reserved = reserved

        def describe_instances(self):
            return self.instances

        def describe_reserved_instances(self, Filters=None):
            final_reserved = {'ReservedInstances': []}
            if Filters is None:
                final_reserved = self.reserved
            else:
                filter = Filters[0]
                if filter['Name'] == 'state':
                    final_reserved['ReservedInstances'] = [
                        reserved_instance
                        for reserved_instance
                        in self.reserved['ReservedInstances']
                        if reserved_instance['State'] not in filter['Values']
                    ]
            return self.reserved

    class MockEC2ClientCall(object):
        def set_responses(self, instances=None, reserved=None):
            if instances is None:
                instances = {}
            if reserved is None:
                reserved = {}
            self.instances = instances
            self.reserved = reserved

        def __call__(self, *args):
            return MockEC2Client(self.instances, self.reserved)

    return MockEC2ClientCall()


@pytest.fixture
def process_ec2():
    class MockProcessEC2(object):
        def set_responses(self, responses=None, unknown=None):
            if responses is None:
                responses = {}
            if unknown is None:
                unknown = []
            self.responses = responses
            self.unknown = unknown

        def __call__(self, url):
            for name in self.unknown:
                warnings.warn("WARN: Parser not implemented for {}"
                              .format(name))
            return self.responses

        def __init__(self, responses=None):
            self.set_responses(responses)

    return MockProcessEC2()


@pytest.fixture
def mock_process_model():
    class MockProcessModel(object):
        def set_responses(self, responses=None):
            if responses is None:
                responses = {}
            self.responses = responses

        def __call__(self, url, instances):
            self.urls.append(url)
            instances.update(self.responses[url])
            return instances

        def __init__(self, responses=None):
            self.urls = []
            self.set_responses(responses)

    return MockProcessModel()


@pytest.fixture
def mock_processor():
    class MockProcessor(object):
        def __call__(self, data, js_name, instances):
            self.data_sets.append(data)
            instances.update(data)
            return instances

        def __init__(self):
            self.data_sets = []

    return MockProcessor()


@pytest.fixture
def mock_process_generic():
    class MockProcessGeneric(object):
        def __call__(self, data, js_name, instances):
            section = accloudtant.aws.prices.SECTION_NAMES[js_name]
            generic = {
                'version': "0.1",
                'kind': section['kind'],
                'key': section['key'],
                }
            instances = instances or {}
            processed_data = {}
            instances.update({section['kind']: processed_data, })
            return generic, instances

    return MockProcessGeneric()
