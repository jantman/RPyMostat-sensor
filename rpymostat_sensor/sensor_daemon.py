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

import logging
from time import sleep
import pkg_resources
import requests

from rpymostat_sensor.sensors.dummy import DummySensor

logger = logging.getLogger(__name__)


class SensorDaemon(object):

    def __init__(self, dry_run=False, dummy_data=False, engine_port=8088,
                 engine_addr=None, interval=60.0):
        """
        Initialize the Sensor Daemon, to read temperatures and send them
        to the Engine API.

        :param dry_run: If True, do not actually send data or perform discovery,
          just log what would be sent.
        :type dry_run: bool
        :param dummy_data: Do not discover or read sensors; instead, send dummy
          sensor data to the Engine.
        :type dummy_data: bool
        :param engine_port: Engine API port
        :type engine_port: int
        :param engine_addr: Engine API address
        :type engine_addr: str
        :param interval: how many seconds to sleep between sensor poll/POST
        :type interval: float
        """
        self.dry_run = dry_run
        self.dummy_data = dummy_data
        self.engine_port = engine_port
        self.engine_addr = engine_addr
        self.interval = interval
        self.host_id = self.find_host_id()
        logger.warning("This machine running with host_id %s", self.host_id)
        if self.dry_run:
            logger.warning("DRY RUN MODE - will not POST data to Engine.")
        if self.engine_addr is None:
            self.engine_addr, self.engine_port = self.discover_engine()
        self.sensors = self.discover_sensors()
        if len(self.sensors) < 1:
            logger.critical("ERROR - no sensors discovered.")
            raise SystemExit(1)

    def run(self):
        """
        Run the Sensor Daemon loop.
        """
        logger.info("Running sensor daemon loop...")
        # loop over reading the sensors, with a sleep interval in-between
        while True:
            self.read_and_send()
            logger.debug("Sleeping %ss", self.interval)
            sleep(self.interval)

    def read_and_send(self):
        """
        Read data from all sensors and send it to the Engine API.
        """
        logger.debug('Reading sensors')
        data = {'host_id': self.host_id, 'sensors': []}
        for sensor in self.sensors:
            val = None
            try:
                val = sensor.read()
                data['sensors'].append(val)
            except:
                logger.exception('Exception reading sensor %s',
                                 sensor.__class__.__name__)
        url = 'http://%s:%s/v1/sensors/update' % (
            self.engine_addr, self.engine_port
        )
        logger.debug('POSTing sensor data to %s: %s', url, data)
        r = requests.post(url, json=data)
        if r.status_code != 202 and r.status_code != 201:
            logger.error('Error POSTing sensor data; got status code %s: %s',
                         r.status_code, r.text)
            return
        logger.info('POSTed sensor data to Engine')

    def discover_engine(self):
        """
        Auto-discover the RPyMostat Engine.

        @TODO this should call a method in RPyMostat-common
        :raises: RuntimeError if discovery fails
        :returns: 2-tuple of engine address (str), engine port (int)
        :rtype: tuple
        """
        raise NotImplementedError("Engine autodiscovery not implemented.")

    def find_host_id(self):
        """
        Find and return a unique Host ID for this physical device.

        @TODO - refactor this out into RPyMostat-common.

        :return: unique host ID
        :rtype: str
        """
        return 'myhostid'

    def dummy_sensor(self):
        """
        Return a list like :py:meth:`~.discover_sensors` that only has a
        :py:class:`~.DummySensor` in it.

        :return: list with a :py:class:`~.DummySensor` instance
        :rtype: list
        """
        return [DummySensor()]

    def _sensor_classes(self):
        """
        Find and instantiate all :py:class:`~.BaseSensor` classes.

        :return: list of :py:class:`~.BaseSensor` instances
        :rtype: list
        """
        if self.dummy_data:
            logger.warning('Running with --dummy - only DummySensor() will '
                           'be loaded')
            return [DummySensor()]
        logger.debug("Loading sensor classes from entry points.")
        classes = []
        for entry_point in pkg_resources.iter_entry_points('rpymostat.sensors'):
            try:
                logger.debug("Trying to load sensor class from entry point: %s",
                             entry_point.name)
                obj = entry_point.load()
                klass = obj()
                classes.append(klass)
            except:
                logger.exception('Exception raised when loading entry point %s',
                                 entry_point.name)
        logger.debug("%s Sensor classes loaded successfully", len(classes))
        return classes

    def discover_sensors(self):
        """
        Returns a list of :py:class:`~.BaseSensor` class instances that have
        reported sensors present.

        :return: list of :py:class:`~.BaseSensor` class instances
        :rtype: list
        """
        have_sensors = []
        logger.debug("Checking sensor classes for sensors...")
        for klass in self._sensor_classes():
            try:
                if klass.sensors_present():
                    logger.info("Sensor class %s.%s reports sensors present",
                                klass.__class__.__module__,
                                klass.__class__.__name__)
                    have_sensors.append(klass)
            except:
                logger.exception('Exception while discovering sensors via '
                                 '%s.%s', klass.__class__.__module__,
                                 klass.__class__.__name__)
        logger.debug("Discovered %d sensor classes with sensors present",
                     len(have_sensors))
        return have_sensors
