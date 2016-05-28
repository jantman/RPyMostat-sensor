"""
The latest version of this package is available at:
<http://github.com/jantman/RPyMostat-sensor>

##################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of RPyMostat-sensor, also known as RPyMostat-sensor.

    RPyMostat-sensor is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RPyMostat-sensor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RPyMostat-sensor.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/RPyMostat-sensor> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

import sys

from rpymostat_sensor.sensors.dummy import DummySensor

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, DEFAULT  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT  # noqa

pbm = 'rpymostat_sensor.sensors.dummy'
pb = '%s.DummySensor' % pbm


class TestDummySensor(object):

    def setup(self):
        self.cls = DummySensor('myhostid')

    def test_sensors_present(self):
        assert self.cls.sensors_present() is True

    def test_read(self):
        with patch('%s.random.choice' % pbm) as mock_choice:
            mock_choice.return_value = 12.34
            res = self.cls.read()
        assert mock_choice.mock_calls == [call(
            [18, 18.25, 18.5, 18.75, 19, 19.25, 19.5, 19.75, 20, 20.25, 20.5,
             20.75, 21, 21.25, 21.5, 21.75, 22, 22.25, 22.5, 22.75, 23, 23.25,
             23.5, 23.75, 24, 24.25, 24.5, 24.75, 25, 25.25, 25.5, 25.75, 26,
             26.25, 26.5, 26.75]
        )]
        assert res == {
            'myhostid_dummy1': {
                'type': 'dummy',
                'value': 12.34,
                'alias': 'dummy'
            }
        }
