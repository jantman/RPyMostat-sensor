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

import abc
import logging

logger = logging.getLogger(__name__)


class BaseSensor(object):
    """
    Base class for the interface that all hardware Sensor classes must
    implement. Any class that implements this interface will be usable to
    discover and read sensors. Note that classes implementing this must also
    have a matching entrypoint in order to be discovered.

    If the class constructor takes any arguments, they must be documented in
    Sphinx format in the docstring of the __init__ method.
    """

    __metaclass__ = abc.ABCMeta

    # One-line string description of the type of sensor this class supports,
    # for use in generated documentation.
    _description = "Unknown"

    def get_description(self):
        """
        Return the sensor class's _description attribute.

        :return: Sensor class's description
        :rtype: str
        """
        return self._description

    @abc.abstractmethod
    def sensors_present(self):
        """
        Discover all matching sensors on the system. Return True if sensors
        were discovered, False otherwise. The class should cache information
        on the discovered sensors in order to read them later.

        :return: whether or not matching sensors are present
        :rtype: bool
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def read(self):
        """
        Read all present temperature sensors. Returns a dict of sensor unique
        IDs (keys) to dicts of sensor information.

        Return dict format:

        .. code-block:: python

            {
                'unique_id_1': {
                    'type': 'sensor_type_string',
                    'value': 1.234,
                    'alias': 'str',
                    'extra': ''
                },
                ...
            }

        Each dict key is a globally-unique sensor ID. Each value is a dict
        with the following keys:

        - type: (str) sensor type
        - value: (float) current temperature in degress Celsius, or None if
           there is an error reading it.
        - alias: (str) a human-readable alias/name for the sensor, if present
        - extra: (str) any extra information about the sensor

        :return: dict of sensor values and information.
        :rtype: dict
        """
        raise NotImplementedError()
