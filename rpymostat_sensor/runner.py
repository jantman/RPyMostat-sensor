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
import logging
import argparse

from rpymostat_sensor.sensor_daemon import SensorDaemon

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


class StoreKeySubKeyValue(argparse.Action):
    """
    Store key=subkey=value options in a dict as {'key': {'subkey': 'value'}}.

    Supports specifying the option multiple times, but NOT with ``nargs``.

    See :py:class:`~argparse.Action`.
    """

    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        super(StoreKeySubKeyValue, self).__init__(
            option_strings, dest, nargs, const, default, type, choices,
            required, help, metavar
        )
        self.default = {}

    def __call__(self, parser, namespace, values, option_string=None):
        if values.count('=') != 2:
            raise argparse.ArgumentError(
                self, 'must be in the form key=subkey=value'
            )
        k, subk, v = values.split('=')
        # handle quotes for values with spaces
        k = k.strip('"\'')
        subk = subk.strip('"\'')
        dest = getattr(namespace, self.dest)
        if k not in dest:
            dest[k] = {}
        dest[k][subk] = v


class Runner(object):

    def parse_args(self, argv):
        """
        parse arguments/options

        :param argv: argument list to parse, usually ``sys.argv[1:]``
        :type argv: list
        :returns: parsed arguments
        :rtype: :py:class:`argparse.Namespace`
        """
        desc = 'RPyMostat Sensor Daemon'
        p = argparse.ArgumentParser(description=desc)
        p.add_argument('-v', '--verbose', dest='verbose', action='count',
                       default=0,
                       help='verbose output. specify twice for debug-level '
                       'output.')
        p.add_argument('-d', '--dry-run', dest='dry_run',
                       action='store_true', default=False,
                       help='Only log results, do not POST to Engine.')
        p.add_argument('-a', '--engine-address', dest='engine_addr',
                       type=str, default=None, help='Engine API address')
        p.add_argument('-p', '--engine-port', dest='engine_port', default=8088,
                       type=int, help='Engine API port')
        p.add_argument('--dummy', dest='dummy', action='store_true',
                       default=False, help='do not discover or read sensors; '
                                           'instead send dummy data')
        p.add_argument('-i', '--interval', dest='interval', default=60.0,
                       type=float, help='Float number of seconds to sleep '
                                        'between sensor poll/POST cycles')
        p.add_argument('-l', '--list-sensor-classes', dest='list_classes',
                       default=False, action='store_true', help='list all '
                       'known sensor classes and their arguments, then exit')
        p.add_argument('-c', '--sensor-class-arg', dest='class_args',
                       action=StoreKeySubKeyValue, help='Provide an argument '
                       'for a specific sensor class, in the form '
                       'ClassName=arg_name=value; see -l for list of classes '
                       'and their arguments')
        args = p.parse_args(argv)
        return args

    def console_entry_point(self):
        """
        Console entry point for RPyMostat-sensor CLI runner - parse args,
        setup logging, run the sensor code.
        """
        args = self.parse_args(sys.argv[1:])
        if args.verbose == 1:
            logger.setLevel(logging.INFO)
        elif args.verbose > 1:
            # debug-level logging hacks
            FORMAT = "[%(levelname)s %(filename)s:%(lineno)s - " \
                     "%(name)s.%(funcName)s() ] %(message)s"
            debug_formatter = logging.Formatter(fmt=FORMAT)
            logger.handlers[0].setFormatter(debug_formatter)
            logger.setLevel(logging.DEBUG)
        if args.list_classes is True:
            d = SensorDaemon(list_classes=True)
            raise SystemExit()
        d = SensorDaemon(
            dry_run=args.dry_run,
            dummy_data=args.dummy,
            engine_port=args.engine_port,
            engine_addr=args.engine_addr,
            interval=args.interval,
            class_args=args.class_args
        )
        d.run()


def console_entry_point():
    """
    Console entry point - instantiate a :py:class:`~.Runner` and call its
    :py:meth:`~.Runner.console_entry_point` method.
    """
    r = Runner()
    try:
        r.console_entry_point()
    except KeyboardInterrupt:
        logger.warning('Exiting on keyboard interrupt.')
        raise SystemExit(0)


if __name__ == "__main__":
    console_entry_point()
