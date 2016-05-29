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
import pytest

from rpymostat_sensor.sensors.owfs import OWFS

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, DEFAULT, mock_open, MagicMock  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT, mock_open, MagicMock  # noqa

pbm = 'rpymostat_sensor.sensors.owfs'
pb = '%s.OWFS' % pbm


class TestOWFS(object):

    def setup(self):
        with patch.multiple(
            pb,
            _discover_owfs=DEFAULT,
            _get_temp_scale=DEFAULT,
        ):
            self.cls = OWFS()
            self.cls.owfs_path = '/my/path'

    def test_init_specified_path(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                _discover_owfs=DEFAULT,
                _get_temp_scale=DEFAULT,
            ) as mocks:
                mocks['_get_temp_scale'].return_value = 'F'
                cls = OWFS(owfs_path='/foo/bar')
        assert mocks['_discover_owfs'].mock_calls == []
        assert mocks['_get_temp_scale'].mock_calls == [call(cls, '/foo/bar')]
        assert mock_logger.mock_calls == [
            call.debug('Using specified owfs_path: %s', '/foo/bar'),
            call.debug('Found OWFS path as %s (temperature scale: %s)',
                       '/foo/bar', 'F')
        ]
        assert cls.owfs_path == '/foo/bar'
        assert cls.temp_scale == 'F'

    def test_init_discover(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                _discover_owfs=DEFAULT,
                _get_temp_scale=DEFAULT,
            ) as mocks:
                mocks['_get_temp_scale'].return_value = 'C'
                mocks['_discover_owfs'].return_value = '/my/path'
                cls = OWFS()
        assert mocks['_discover_owfs'].mock_calls == [call(cls)]
        assert mocks['_get_temp_scale'].mock_calls == [call(cls, '/my/path')]
        assert mock_logger.mock_calls == [
            call.debug('Discovered OWFS path as: %s', '/my/path'),
            call.debug('Found OWFS path as %s (temperature scale: %s)',
                       '/my/path', 'C')
        ]
        assert cls.owfs_path == '/my/path'
        assert cls.temp_scale == 'C'

    def test_init_discover_failed(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                _discover_owfs=DEFAULT,
                _get_temp_scale=DEFAULT,
            ) as mocks:
                mocks['_get_temp_scale'].return_value = 'C'
                mocks['_discover_owfs'].return_value = None
                with pytest.raises(RuntimeError) as excinfo:
                    OWFS()
        assert mocks['_discover_owfs'].call_count == 1
        assert mocks['_get_temp_scale'].mock_calls == []
        assert mock_logger.mock_calls == [
            call.debug('Discovered OWFS path as: %s', None)
        ]
        if sys.version_info[0] > 2:
            msg = excinfo.value.args[0]
        else:
            msg = excinfo.value.message
        assert msg == 'Could not discover OWFS mountpoint and owfs_path ' \
                      'class argument not specified.'

    def test_discover_owfs(self):
        self.cls.owfs_paths = ['/foo', '/bar', '/baz']

        def se_exists(path):
            if path.startswith('/baz'):
                return True
            if path == '/bar':
                return True
            return False

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.os.path.exists' % pbm, autospec=True) as mock_ex:
                mock_ex.side_effect = se_exists
                res = self.cls._discover_owfs()
        assert res == '/baz'
        assert mock_ex.mock_calls == [
            call('/foo'),
            call('/bar'),
            call('/bar/settings/units/temperature_scale'),
            call('/baz'),
            call('/baz/settings/units/temperature_scale')
        ]
        assert mock_logger.mock_calls == [
            call.debug('Attempting to find OWFS path/mountpoint from list '
                       'of common options: %s', ['/foo', '/bar', '/baz']),
            call.debug('Path %s does not exist; skipping', '/foo'),
            call.debug('Path %s exists but does not appear to have OWFS '
                       'mounted', '/bar'),
            call.info('Found OWFS mounted at: %s', '/baz')
        ]

    def test_discover_owfs_none(self):
        self.cls.owfs_paths = ['/foo', '/bar', '/baz']

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.os.path.exists' % pbm, autospec=True) as mock_ex:
                mock_ex.return_value = False
                res = self.cls._discover_owfs()
        assert res is None
        assert mock_ex.mock_calls == [
            call('/foo'),
            call('/bar'),
            call('/baz'),
        ]
        assert mock_logger.mock_calls == [
            call.debug('Attempting to find OWFS path/mountpoint from list '
                       'of common options: %s', ['/foo', '/bar', '/baz']),
            call.debug('Path %s does not exist; skipping', '/foo'),
            call.debug('Path %s does not exist; skipping', '/bar'),
            call.debug('Path %s does not exist; skipping', '/baz'),
            call.debug('Could not discover any OWFS at known mountpoints')
        ]

    def test_get_temp_scale(self):
        with patch('%s.open' % pbm, mock_open(read_data='F ')) as mock_opn:
            res = self.cls._get_temp_scale('/foo/bar')
        assert res == 'F'
        assert mock_opn.mock_calls == [
            call('/foo/bar/settings/units/temperature_scale', 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None)
        ]

    def test_sensors_present_true(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s._find_sensors' % pb, autospec=True) as mock_find:
                mock_find.return_value = ['A', 'B']
                res = self.cls.sensors_present()
        assert res is True
        assert mock_find.mock_calls == [call(self.cls)]
        assert mock_logger.mock_calls == [
            call.debug('Found %d sensors present: %s', 2, ['A', 'B'])
        ]

    def test_sensors_present_false(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s._find_sensors' % pb, autospec=True) as mock_find:
                mock_find.return_value = []
                res = self.cls.sensors_present()
        assert res is False
        assert mock_find.mock_calls == [call(self.cls)]
        assert mock_logger.mock_calls == [
            call.debug('Found %d sensors present: %s', 0, [])
        ]

    def test_find_sensors(self):
        self.cls.owfs_path = '/my/path'

        def se_read(klass, sensor_dir, fname):
            if sensor_dir == '10.58F50F010800':
                if fname == 'address':
                    return '1058F50F01080047'
                if fname == 'type':
                    return 'DS18S20'
            if sensor_dir == '10.58F50F020800':
                if fname == 'address':
                    return '1058F50F02080047'
                if fname == 'alias':
                    return 'myalias'
            return None

        def se_isdir(path):
            dirs = [
                '/my/path/10.58F50F010800',
                '/my/path/10.58F50F020800',
                '/my/path/81.C1252A000000',
                '/my/path/alarm'
            ]
            if path in dirs:
                return True
            return False

        def se_exists(path):
            exist = [
                '/my/path/10.58F50F010800',
                '/my/path/10.58F50F010800/temperature',
                '/my/path/10.58F50F020800',
                '/my/path/10.58F50F020800/temperature',
                '/my/path/10.58F50F020800/alias',
                '/my/path/81.C1252A000000',
                '/my/path/alarm'
            ]
            if path in exist:
                return True
            return False

        dirlist = [
            '10.58F50F010800',
            '10.58F50F020800',
            '81.C1252A000000',
            'alarm',
            'foo'
        ]
        mock_fh = MagicMock(create=True)
        mock_fh.read.side_effect = se_read

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.os.listdir' % pbm, autospec=True) as mock_listdir:
                mock_listdir.return_value = dirlist
                with patch('%s.os.path.isdir' % pbm,
                           autospec=True) as mock_isdir:
                    mock_isdir.side_effect = se_isdir
                    with patch('%s.os.path.exists' % pbm,
                               autospec=True) as mock_exists:
                        mock_exists.side_effect = se_exists
                        with patch(
                            '%s._read_owfs_file' % pb, autospec=True
                        ) as mock_read:
                            mock_read.side_effect = se_read
                            res = self.cls._find_sensors()
        assert res == [
            {
                'temp_path': '/my/path/10.58F50F010800/temperature',
                'address': '1058F50F01080047',
                'type': 'DS18S20'
            },
            {
                'temp_path': '/my/path/10.58F50F020800/temperature',
                'address': '1058F50F02080047',
                'alias': 'myalias',
            }
        ]
        assert mock_listdir.mock_calls == [call('/my/path')]
        assert mock_isdir.mock_calls == [
            call('/my/path/10.58F50F010800'),
            call('/my/path/10.58F50F020800'),
            call('/my/path/81.C1252A000000'),
            call('/my/path/alarm'),
            call('/my/path/foo')
        ]
        assert mock_exists.mock_calls == [
            call('/my/path/10.58F50F010800/temperature'),
            call('/my/path/10.58F50F020800/temperature'),
            call('/my/path/81.C1252A000000/temperature')
        ]
        assert mock_read.mock_calls == [
            call(self.cls, '10.58F50F010800', 'address'),
            call(self.cls, '10.58F50F010800', 'alias'),
            call(self.cls, '10.58F50F010800', 'type'),
            call(self.cls, '10.58F50F020800', 'address'),
            call(self.cls, '10.58F50F020800', 'alias'),
            call(self.cls, '10.58F50F020800', 'type')
        ]
        assert mock_logger.mock_calls == [
            call.debug('found temperature sensor at: %s',
                       '/my/path/10.58F50F010800/temperature'),
            call.debug('found temperature sensor at: %s',
                       '/my/path/10.58F50F020800/temperature'),
        ]

    def test_read_owfs_file(self):
        d = '  foo bar '
        with patch('%s.os.path.exists' % pbm, autospec=True) as mock_exists:
            mock_exists.return_value = True
            with patch('%s.open' % pbm, mock_open(read_data=d)) as mock_opn:
                res = self.cls._read_owfs_file('sdir', 'foo')
        assert res == 'foo bar'
        assert mock_exists.mock_calls == [call('/my/path/sdir/foo')]
        assert mock_opn.mock_calls == [
            call('/my/path/sdir/foo', 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None)
        ]

    def test_read_owfs_file_no_exist(self):
        d = '  foo bar '
        with patch('%s.os.path.exists' % pbm, autospec=True) as mock_exists:
            mock_exists.return_value = False
            with patch('%s.open' % pbm, mock_open(read_data=d)) as mock_opn:
                res = self.cls._read_owfs_file('sdir', 'foo')
        assert res is None
        assert mock_exists.mock_calls == [call('/my/path/sdir/foo')]
        assert mock_opn.mock_calls == []

    def test_read_owfs_file_empty(self):
        d = ' '
        with patch('%s.os.path.exists' % pbm, autospec=True) as mock_exists:
            mock_exists.return_value = True
            with patch('%s.open' % pbm, mock_open(read_data=d)) as mock_opn:
                res = self.cls._read_owfs_file('sdir', 'foo')
        assert res is None
        assert mock_exists.mock_calls == [call('/my/path/sdir/foo')]
        assert mock_opn.mock_calls == [
            call('/my/path/sdir/foo', 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None)
        ]

    def test_read_owfs_file_exception(self):

        exc = Exception()

        def se_exc(*args):
            raise exc

        mock_read = mock_open()
        mock_read.return_value.read.side_effect = se_exc

        with patch('%s.os.path.exists' % pbm, autospec=True) as mock_exists:
            mock_exists.return_value = True
            with patch('%s.open' % pbm, mock_read, create=True) as mock_opn:
                with patch('%s.logger' % pbm, autospec=True) as mock_logger:
                    res = self.cls._read_owfs_file('sdir', 'foo')
        assert res is None
        assert mock_exists.mock_calls == [call('/my/path/sdir/foo')]
        assert len(mock_opn.mock_calls) == 4
        assert mock_opn.mock_calls[0] == call('/my/path/sdir/foo', 'r')
        assert mock_logger.mock_calls == [
            call.debug('Exception reading %s', '/my/path/sdir/foo', exc_info=1)
        ]

    def test_read(self):
        """
        there's some crazyness here trying to mock open() with different return
        values depending on the path
        """
        sensors = [
            {
                'address': 'sensor1',
                'temp_path': '/foo/bar/one'
            },
            {
                'type': 'mytype',
                'alias': 'myalias',
                'address': 'sensor2',
                'temp_path': '/foo/bar/two'
            },
            {
                'address': 'sensor3',
                'temp_path': '/foo/bar/three'
            }
        ]

        exc = Exception()

        def se_exc(*args):
            raise exc

        mock_one = MagicMock(name='mock_one')
        mock_one.__enter__.return_value.read.return_value = '11.234'
        m_one = mock_open(mock=mock_one)

        mock_two = MagicMock(name='mock_two')
        mock_two.__enter__.return_value.read.return_value = '22.567'
        m_two = mock_open(mock=mock_two)

        mock_three = MagicMock(name='mock_three')
        mock_three.__enter__.return_value.read.side_effect = se_exc
        m_three = mock_open(mock=mock_three)

        mock_other = MagicMock(name='mock_other')
        mock_other.__enter__.return_value.read.return_value = '999.99'
        m_other = mock_open(mock=mock_other)

        def se_opn(*args):
            print(args)
            if args[0] == '/foo/bar/one':
                return m_one
            if args[0] == '/foo/bar/two':
                return m_two
            if args[0] == '/foo/bar/three':
                return m_three
            return m_other

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s._find_sensors' % pb, autospec=True) as mock_find:
                with patch('%s.open' % pbm, create=True) as mock_opn:
                    mock_opn.side_effect = se_opn
                    mock_find.return_value = sensors
                    res = self.cls.read()
        assert mock_find.mock_calls == [call(self.cls)]
        assert mock_opn.mock_calls == [
            call('/foo/bar/one', 'r'),
            call('/foo/bar/two', 'r'),
            call('/foo/bar/three', 'r')
        ]
        assert m_one.mock_calls == [
            call.__enter__(),
            call.__enter__().read(),
            call.__exit__(None, None, None)
        ]
        assert m_two.mock_calls == [
            call.__enter__(),
            call.__enter__().read(),
            call.__exit__(None, None, None)
        ]
        # third arg to third call is a traceback, so assert about everything
        # else
        assert len(m_three.mock_calls) == 3
        assert m_three.mock_calls[0] == call.__enter__()
        assert m_three.mock_calls[1] == call.__enter__().read()
        # third call is __exit__
        assert m_three.mock_calls[2][0] == '__exit__'
        # first and second args to that third call...
        assert m_three.mock_calls[2][1][0] == type(exc)
        assert m_three.mock_calls[2][1][1] == exc
        assert m_other.mock_calls == []
        assert mock_logger.mock_calls == [
            call.debug('Reading temperature from sensor %s at %s', 'sensor1',
                       '/foo/bar/one'),
            call.debug('Got temperature of %s from %s', 11.234, 'sensor1'),
            call.debug('Reading temperature from sensor %s at %s', 'sensor2',
                       '/foo/bar/two'),
            call.debug('Got temperature of %s from %s', 22.567, 'sensor2'),
            call.debug('Reading temperature from sensor %s at %s', 'sensor3',
                       '/foo/bar/three'),
            call.debug('Exception reading from sensor %s', 'sensor3',
                       exc_info=1)
        ]
        assert res == {
            'sensor1': {
                'type': None,
                'value': 11.234
            },
            'sensor2': {
                'type': 'mytype',
                'alias': 'myalias',
                'value': 22.567
            },
            'sensor3': {
                'type': None,
                'value': None
            }
        }
