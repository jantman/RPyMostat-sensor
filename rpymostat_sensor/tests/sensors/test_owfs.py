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
    from mock import patch, call, Mock, DEFAULT, mock_open  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT, mock_open  # noqa

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
