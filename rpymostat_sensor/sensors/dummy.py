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

import random

from rpymostat_sensor.sensors.base import BaseSensor


class DummySensor(BaseSensor):
    """
    Dummy sensor class that returns random temperatures.
    """

    def __init__(self, host_id):
        """
        Initialize dummy sensor.

        :param host_id: unique ID of this host.
        :type host_id: str
        """
        self.host_id = host_id

    def sensors_present(self):
        """
        Discover a single dummy temperature sensor.

        :return: True because it's always here
        :rtype: bool
        """
        return True

    def read(self):
        """
        Returns a dict, where the value is a pseudo-random float in the range
        of 18 to 26.75 (inclusive) incremented by .25.

        Return dict format:

        .. code-block:: python

            {
                '<self.host_id>_dummy1': {
                    'type': 'dummy',
                    'value': <value>,
                    'alias': 'dummy'
                }
            }

        :return: dict of sensor values and information.
        :rtype: dict
        """
        choices = []
        for x in range(18, 27):
            for y in [0, 0.25, 0.5, 0.75]:
                choices.append(x + y)
        val = random.choice(choices)
        return {
            '%s_dummy1' % self.host_id: {
                'type': 'dummy',
                'value': val,
                'alias': 'dummy'
            }
        }
