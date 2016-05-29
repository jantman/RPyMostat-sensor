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
import pkg_resources

from rpymostat_sensor.sensors.base import BaseSensor

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, DEFAULT  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT  # noqa


class TestSensor(BaseSensor):

    _description = 'foo desc'

    def __init__(self, argOne, argTwo, kwarg1=None, kwarg2=1234):
        """
        Some text here
        About the init function

        Foo

        Bar.

        :param argOne: arg one info
        :type argOne: str
        :param argTwo: arg two info is a
          long
          line
        :type arg2: int
        :param kwarg1: kwarg1 info
        :type kwarg1: str
        :param kwarg2: kwarg2 info
        :return: foo
        """
        pass

    def sensors_present(self):
        return True

    def read(self):
        return {}


class TestBaseSensor(object):

    def setup(self):
        self.cls = TestSensor('one', 'two')

    def test_get_description(self):
        assert self.cls.get_description() == 'foo desc'


class TestAllSensorClasses(object):

    def base_class_tester(self, entry_point):
        klass = entry_point.load()
        assert klass._description != 'Unknown'

    def test_all(self):
        for entry_point in pkg_resources.iter_entry_points('rpymostat.sensors'):
            yield 'entry_point %s' % entry_point.name, self.base_class_tester, \
                  entry_point
