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
from rpymostat_common.unique_ids import SystemID
from rpymostat_common.discovery import discover_engine as utils_discover_engine


logger = logging.getLogger(__name__)


class SensorDaemon(object):

    def __init__(self, dry_run=False, dummy_data=False, engine_port=8088,
                 engine_addr=None, interval=60.0, list_classes=False,
                 class_args={}):
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
        :param list_classes: if True, list all discovered classes and their
          args, then raise SystemExit()
        :type list_classes: bool
        :param class_args: dict of optional arguments to pass to sensor classes
          init method; of the form {'ClassName': {'arg_name': 'value'}}
        :type class_args: dict
        """
        if list_classes:
            self.list_classes()
            raise SystemExit()
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
        self.sensors = self.discover_sensors(class_args)
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
        data = {'host_id': self.host_id, 'sensors': {}}
        for sensor in self.sensors:
            try:
                for s_id, s_data in sensor.read().iteritems():
                    data['sensors'][s_id] = s_data
            except:
                logger.exception('Exception reading sensor %s',
                                 sensor.__class__.__name__)
        url = 'http://%s:%s/v1/sensors/update' % (
            self.engine_addr, self.engine_port
        )
        try:
            logger.debug('POSTing sensor data to %s: %s', url, data)
            r = requests.post(url, json=data)
            if r.status_code != 202 and r.status_code != 201:
                logger.error('Error POSTing sensor data; got status code %s: '
                             '%s', r.status_code, r.text)
                return
        except:
            logger.exception('Exception caught when trying to POST data to '
                             'Engine; will try again at next interval.')
            return None
        logger.info('POSTed sensor data to Engine')

    def discover_engine(self):
        """
        Auto-discover the RPyMostat Engine.

        :returns: 2-tuple of engine address (str), engine port (int)
        :rtype: tuple
        """
        ea, ep = utils_discover_engine()
        logger.info("Discovered Engine at %s:%s", ea, ep)
        return ea, ep

    def find_host_id(self):
        """
        Find and return a unique Host ID for this physical device.

        @TODO - refactor this out into RPyMostat-common.

        :return: unique host ID
        :rtype: str
        """
        return SystemID().id_string

    def _sensor_classes(self):
        """
        Find and instantiate all :py:class:`~.BaseSensor` classes.

        :return: list of :py:class:`~.BaseSensor` instances
        :rtype: list
        """
        logger.debug("Loading sensor classes from entry points.")
        classes = []
        for entry_point in pkg_resources.iter_entry_points('rpymostat.sensors'):
            try:
                logger.debug("Trying to load sensor class from entry point: %s",
                             entry_point.name)
                obj = entry_point.load()
                classes.append(obj)
            except:
                logger.debug('Exception raised when loading entry point %s',
                             entry_point.name, exc_info=1)
        logger.debug("%s Sensor classes loaded successfully: %s", len(classes),
                     [c.__name__ for c in classes])
        return classes

    def discover_sensors(self, class_args={}):
        """
        Returns a list of :py:class:`~.BaseSensor` class instances that have
        reported sensors present.

        :param class_args: dict of optional arguments to pass to sensor classes
          init method; of the form {'ClassName': {'arg_name': 'value'}}
        :type class_args: dict
        :return: list of :py:class:`~.BaseSensor` class instances
        :rtype: list
        """
        if self.dummy_data:
            logger.warning('Running with --dummy - only DummySensor() will '
                           'be loaded')
            return [DummySensor(self.host_id)]
        have_sensors = []
        logger.debug("Checking sensor classes for sensors...")
        for klass in self._sensor_classes():
            kwargs = {}
            if klass.__class__.__name__ in class_args:
                kwargs = class_args[klass.__class__.__name__]
            try:
                cls = klass(**kwargs)
            except:
                logger.debug('Exception while instantiating sensor class %s '
                             'with kwargs=%s', klass.__class__.__name__, kwargs,
                             exc_info=1)
                continue
            try:
                if cls.sensors_present():
                    logger.info("Sensor class %s.%s reports sensors present",
                                cls.__class__.__module__,
                                cls.__class__.__name__)
                    have_sensors.append(cls)
            except:
                logger.debug('Exception while discovering sensors via '
                             '%s.%s', cls.__class__.__module__,
                             cls.__class__.__name__, exc_info=1)
        logger.debug("Discovered %d sensor classes with sensors present",
                     len(have_sensors))
        return have_sensors

    def list_classes(self):
        """
        Print a list of sensor class names, along with their _description
        attributes (if present) and any arguments they accept.
        """
        pass
