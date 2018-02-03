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


@pytest.fixture
def mock_requests_get():
    class MockRequestsGet(object):
        def set_responses(self, responses=None):
            if responses is None:
                responses = {}
            self.responses = responses

        def __call__(self, url):
            self.urls.append(url)
            if url in self.responses:
                self.text = self.responses[url]
            else:
                self.text = 'Default response'
            self.content = self.text.encode('utf-8')
            return self

        def __init__(self, responses=None):
            self.set_responses(responses)
            self.urls = []
            self.text = 'Default response'

    return MockRequestsGet()
