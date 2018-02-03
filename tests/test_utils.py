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

import re
import codecs
import accloudtant.utils


def test_extract_data(monkeypatch, mock_requests_get):
    fixture_dir = 'tests/aws/fixtures/'
    source_file = 'current_generation_on_demand.html'
    source = ""
    with open('{}{}'.format(fixture_dir, source_file)) as input_file:
        source = input_file.read()

    base = 'http://a0.awsstatic.com/pricing/1/ec2/'
    expected_urls = [
        '{}linux-od.min.js'.format(base),
        '{}rhel-od.min.js'.format(base),
        '{}sles-od.min.js'.format(base),
        '{}mswin-od.min.js'.format(base),
        '{}mswinSQL-od.min.js'.format(base),
        '{}mswinSQLWeb-od.min.js'.format(base),
        '{}mswinSQLEnterprise-od.min.js'.format(base),
        '{}pricing-data-transfer-with-regions.min.js'.format(base),
        '{}pricing-ebs-optimized-instances.min.js'.format(base),
        '{}pricing-elastic-ips.min.js'.format(base),
    ]

    def get_url(line):
        return re.sub(r".+'(.+)'.*", r"http:\1", line.strip())

    url = 'https://aws.amazon.com/ec2/pricing/on-demand'

    monkeypatch.setattr('requests.get', mock_requests_get)
    mock_requests_get.set_responses({
        url: source,
    })

    urls = list(accloudtant.utils.extract_data(url, 'model:', get_url))

    assert(urls == expected_urls)


def test_fix_lazy_json():
    bad_json = '{ key: "value" }'.encode('utf-8')
    good_json = '{"key":"value"}'
    result = accloudtant.utils.fix_lazy_json(codecs.decode(bad_json))
    assert(result == good_json)
