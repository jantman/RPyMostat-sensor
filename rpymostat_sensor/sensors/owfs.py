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

import os
import logging
import re
from rpymostat_sensor.sensors.base import BaseSensor

logger = logging.getLogger(__name__)


class OWFS(BaseSensor):
    """
    Sensor class to read OWFS sensors. Currently only tested with DS18S20.
    """

    # list of filesystem paths to check when attempting to discover OWFS
    owfs_paths = [
        '/run/owfs',
        '/owfs',
        '/mnt/owfs',
        '/var/owfs',
        '/1wire',
        '/var/1wire',
        '/mnt/1wire',
        '/run/1wire'
    ]

    sensor_dir_re = re.compile(r'^[0-9a-fA-F]+\.[0-9a-fA-F]+$')

    def __init__(self, owfs_path=None):
        """
        Initialize sensor class to read OWFS sensors.

        :param owfs_path: Absolute path to the OWFS mountpoint. If not
          specified, some common defaults will be tried.
        :type owfs_path: str
        """
        super(OWFS)
        if owfs_path is None:
            owfs_path = self._discover_owfs()
            logger.debug('Discovered OWFS path as: %s', owfs_path)
        else:
            logger.debug('Using specified owfs_path: %s', owfs_path)
        if owfs_path is None:
            raise RuntimeError('Could not discover OWFS mountpoint and '
                               'owfs_path class argument not specified.')
        self.owfs_path = owfs_path
        self.temp_scale = self._get_temp_scale(self.owfs_path)
        logger.debug('Found OWFS path as %s (temperature scale: %s)',
                     self.owfs_path, self.temp_scale)

    def _discover_owfs(self):
        """
        If ``owfs_path`` is not specified for :py:meth:`.__init__`, attempt
        to find an OWFS mounted at some of the common paths. If one is found,
        return the path to it. If not, return None.

        :return: path to OWFS mountpoint or None
        """
        logger.debug('Attempting to find OWFS path/mountpoint from list of '
                     'common options: %s', self.owfs_paths)
        for path in self.owfs_paths:
            if not os.path.exists(path):
                logger.debug('Path %s does not exist; skipping', path)
                continue
            if not os.path.exists(
                    os.path.join(path, 'settings', 'units', 'temperature_scale')
            ):
                logger.debug('Path %s exists but does not appear to have '
                             'OWFS mounted', path)
                continue
            logger.info('Found OWFS mounted at: %s', path)
            return path
        logger.debug('Could not discover any OWFS at known mountpoints')
        return None

    def _get_temp_scale(self, owfs_path):
        """
        Read and return the temperature_scale setting in use by OWFS mounted at
        owfs_path.

        :param owfs_path: OWFS mountpoint
        :type owfs_path: str
        :return: temperature scale in use ('C', 'F', 'K', or 'R')
        :rtype: str
        """
        scale_path = os.path.join(
            owfs_path, 'settings', 'units', 'temperature_scale'
        )
        with open(scale_path, 'r') as fh:
            scale = fh.read().strip()
        return scale

    def sensors_present(self):
        """
        Determine whethere there are OWFS temperature sensors present or not.

        :return: True because it's always here
        :rtype: bool
        """
        sensors = self._find_sensors()
        logger.debug('Found %d sensors present: %s', len(sensors), sensors)
        if len(sensors) > 0:
            return True
        return False

    def _find_sensors(self):
        """
        Find all OWFS temperature sensors present. Return a list of dicts of
        information about them. Dicts have the format:

        {
            'temp_path': 'absolute path to read temperature from',
            'alias': 'sensor alias, if set',
            'address': 'sensor address',
            'type': 'sensor type'
        }

        The only *required* key in the dict is ``temp_path``.

        :return: list of dicts describing present temperature sensors.
        :rtype: dict
        """
        sensors = []
        for subdir in os.listdir(self.owfs_path):
            # skip if it's not a directory
            if not os.path.isdir(os.path.join(self.owfs_path, subdir)):
                continue
            # skip if it doesn't match the sensor regex
            if not self.sensor_dir_re.match(subdir):
                continue
            # skip if it doesn't have a temperature subdir
            temp_path = os.path.join(self.owfs_path, subdir, 'temperature')
            if not os.path.exists(temp_path):
                continue
            # looks like a temperature sensor; add what we can to the dict
            logger.debug('found temperature sensor at: %s', temp_path)
            d = {
                'temp_path': temp_path,
                'address': self._read_owfs_file(subdir, 'address')
            }
            alias = self._read_owfs_file(subdir, 'alias')
            if alias is not None:
                d['alias'] = alias
            _type = self._read_owfs_file(subdir, 'type')
            if _type is not None:
                d['type'] = _type
            sensors.append(d)
        return sensors

    def _read_owfs_file(self, sensor_dir, fname):
        """
        Read the contents of a file from OWFS; return None if the file does
        not exist, or the strip()'ed contents if it does. Really just a helper
        for cleaner unit testing.

        :param sensor_dir: ``self.owfs_path`` subdir for the sensor
        :type sensor_dir: str
        :param fname: file name/path under ``sensor_dir``
        :type fname: str
        :return: stripped content str or None
        """
        path = os.path.join(self.owfs_path, sensor_dir, fname)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as fh:
                tmp = fh.read().strip()
        except Exception:
            logger.debug('Exception reading %s', path, exc_info=1)
            return None
        if tmp == '':
            return None
        return tmp

    def read(self):
        """
        Read all present temperature sensors.

        Returns a dict of sensor unique IDs (keys) to dicts of sensor
        information.

        Return dict format:

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
        res = {}
        sensors = self._find_sensors()
        for sensor in sensors:
            data = {'type': sensor.get('type', None)}
            if 'alias' in sensor and sensor['alias'] is not None:
                data['alias'] = sensor['alias']
            try:
                logger.debug('Reading temperature from sensor %s at %s',
                             sensor['address'], sensor['temp_path'])
                with open(sensor['temp_path'], 'r') as fh:
                    temp = fh.read().strip()
                data['value'] = float(temp)
                logger.debug('Got temperature of %s from %s', data['value'],
                             sensor['address'])
            except:
                logger.debug('Exception reading from sensor %s',
                             sensor['address'], exc_info=1)
                data['value'] = None
            res[sensor['address']] = data
        return res
