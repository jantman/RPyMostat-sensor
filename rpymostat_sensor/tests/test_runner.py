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

from rpymostat_sensor.runner import console_entry_point, Runner

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, DEFAULT  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT  # noqa

pbm = 'rpymostat_sensor.runner'
pb = '%s.Runner' % pbm


class TestConsoleEntryPoint(object):

    def test_console_entry_point(self):
        with patch(pb, autospec=True) as mock_runner:
            console_entry_point()
        assert mock_runner.mock_calls == [
            call(),
            call().console_entry_point()
        ]


class TestRunner(object):

    def setup(self):
        self.cls = Runner()

    def test_parse_args_argparse(self):
        argv = Mock()
        parse_res = Mock()
        with patch('%s.argparse.ArgumentParser' % pbm, autospec=True) as mock_p:
            mock_p.return_value.parse_args.return_value = parse_res
            res = self.cls.parse_args(argv)
        assert res == parse_res
        assert mock_p.mock_calls == [
            call(description='RPyMostat Sensor Daemon'),
            call().add_argument('-v', '--verbose', dest='verbose',
                                action='count', default=0,
                                help='verbose output. specify twice for '
                                     'debug-level output.'),
            call().add_argument('-d', '--dry-run', dest='dry_run',
                                action='store_true', default=False,
                                help='Only log results, do not POST to Engine.'
                                ),
            call().add_argument('-a', '--engine-address', dest='engine_addr',
                                type=str, default=None,
                                help='Engine API address'),
            call().add_argument('-p', '--engine-port', dest='engine_port',
                                default=8088, type=int, help='Engine API port'),
            call().add_argument('--dummy', dest='dummy', action='store_true',
                                default=False, help='do not discover or read '
                                'sensors; instead send dummy data'),
            call().add_argument('-i', '--interval', dest='interval',
                                default=60.0, type=float,
                                help='Float number of seconds to sleep '
                                'between sensor poll/POST cycles'),
            call().parse_args(argv)
        ]

    def test_parse_args_default(self):
        res = self.cls.parse_args([])
        assert res.verbose == 0
        assert res.dry_run is False
        assert res.engine_addr is None
        assert res.engine_port == 8088
        assert res.dummy is False
        assert res.interval == 60.0

    def test_parse_args_nondefault(self):
        res = self.cls.parse_args([
            '-v',
            '--dry-run',
            '-a', 'foo.bar.baz',
            '--engine-port=1234',
            '--dummy',
            '-i', '12.34'
        ])
        assert res.verbose == 1
        assert res.dry_run is True
        assert res.engine_addr == 'foo.bar.baz'
        assert res.engine_port == 1234
        assert res.dummy is True
        assert res.interval == 12.34

    def test_parse_args_verbose2(self):
        res = self.cls.parse_args(['-vv'])
        assert res.verbose == 2
        assert res.dry_run is False
        assert res.engine_addr is None
        assert res.engine_port == 8088
        assert res.dummy is False
        assert res.interval == 60.0

    def test_console_entry_point_defaults(self):
        mock_args = Mock(
            verbose=0,
            dry_run=False,
            engine_addr=None,
            engine_port=8088,
            dummy=False,
            interval=60.0
        )
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                parse_args=DEFAULT,
            ) as mocks:
                mocks['parse_args'].return_value = mock_args
                with patch('%s.SensorDaemon' % pbm,
                           autospec=True) as mock_daemon:
                    self.cls.console_entry_point()
        assert mock_logger.mock_calls == []
        assert mock_daemon.mock_calls == [
            call(
                dry_run=False,
                dummy_data=False,
                engine_port=8088,
                engine_addr=None,
                interval=60.0
            ),
            call().run()
        ]

    def test_console_entry_point_verbose1(self):
        mock_args = Mock(
            verbose=1,
            dry_run=True,
            engine_addr='foo.bar.baz',
            engine_port=5678,
            dummy=True,
            interval=123.45
        )
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                parse_args=DEFAULT,
            ) as mocks:
                mocks['parse_args'].return_value = mock_args
                with patch('%s.SensorDaemon' % pbm,
                           autospec=True) as mock_daemon:
                    self.cls.console_entry_point()
        assert mock_logger.mock_calls == [
            call.setLevel(logging.INFO)
        ]
        assert mock_daemon.mock_calls == [
            call(
                dry_run=True,
                dummy_data=True,
                engine_port=5678,
                engine_addr='foo.bar.baz',
                interval=123.45
            ),
            call().run()
        ]

    def test_console_entry_point_verbose2(self):
        mock_args = Mock(
            verbose=2,
            dry_run=False,
            engine_addr=None,
            engine_port=8088,
            dummy=False,
            interval=60.0
        )
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                parse_args=DEFAULT,
            ) as mocks:
                mocks['parse_args'].return_value = mock_args
                with patch('%s.SensorDaemon' % pbm,
                           autospec=True) as mock_daemon:
                    with patch('%s.logging.Formatter' % pbm,
                               autospec=True) as mock_formatter:
                        mock_handler = Mock(spec_set=logging.Handler)
                        type(mock_logger).handlers = [mock_handler]
                        self.cls.console_entry_point()
        FORMAT = "[%(levelname)s %(filename)s:%(lineno)s - " \
                 "%(name)s.%(funcName)s() ] %(message)s"
        assert mock_formatter.mock_calls == [
            call(fmt=FORMAT),
        ]
        assert mock_handler.mock_calls == [
            call.setFormatter(mock_formatter.return_value)
        ]
        assert mock_logger.mock_calls == [
            call.setLevel(logging.DEBUG)
        ]
        assert mock_daemon.mock_calls == [
            call(
                dry_run=False,
                dummy_data=False,
                engine_port=8088,
                engine_addr=None,
                interval=60.0
            ),
            call().run()
        ]
