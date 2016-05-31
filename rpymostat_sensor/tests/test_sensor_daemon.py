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

from rpymostat_sensor.sensor_daemon import SensorDaemon
from rpymostat_sensor.sensors.dummy import DummySensor
from rpymostat_sensor.sensors.base import BaseSensor

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, DEFAULT, PropertyMock, MagicMock  # noqa
else:
    from unittest.mock import patch, call, Mock, DEFAULT, PropertyMock, MagicMock  # noqa

pbm = 'rpymostat_sensor.sensor_daemon'
pb = '%s.SensorDaemon' % pbm


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


class TestSensorDaemon(object):

    def setup(self):
        with patch.multiple(
            pb,
            autospec=True,
            find_host_id=DEFAULT,
            discover_engine=DEFAULT,
            discover_sensors=DEFAULT,
        ) as mocks:
            mocks['find_host_id'].return_value = 'myhostid'
            mocks['discover_engine'].return_value = ('foo.bar.baz', 1234)
            mocks['discover_sensors'].return_value = {
                'sensor1': {'foo': 'bar'}
            }
            self.cls = SensorDaemon()

    def test_init_default(self):
        sensors = [Mock(), Mock()]
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                find_host_id=DEFAULT,
                discover_engine=DEFAULT,
                discover_sensors=DEFAULT,
                list_classes=DEFAULT,
            ) as mocks:
                mocks['find_host_id'].return_value = 'myhostid'
                mocks['discover_engine'].return_value = ('foo.bar.baz', 1234)
                mocks['discover_sensors'].return_value = sensors
                cls = SensorDaemon()
        assert cls.dry_run is False
        assert cls.dummy_data is False
        assert cls.engine_port == 1234
        assert cls.engine_addr == 'foo.bar.baz'
        assert cls.interval == 60.0
        assert cls.host_id == 'myhostid'
        assert cls.sensors == sensors
        assert mock_logger.mock_calls == [
            call.warning('This machine running with host_id %s', 'myhostid')
        ]
        assert mocks['find_host_id'].mock_calls == [call(cls)]
        assert mocks['discover_engine'].mock_calls == [call(cls)]
        assert mocks['discover_sensors'].mock_calls == [call(cls, {})]
        assert mocks['list_classes'].mock_calls == []

    def test_init_list_classes(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                find_host_id=DEFAULT,
                discover_engine=DEFAULT,
                discover_sensors=DEFAULT,
            ) as mocks:
                with pytest.raises(SystemExit):
                    with patch('%s.list_classes' % pb) as mock_list:
                        SensorDaemon(list_classes=True)
        assert mock_logger.mock_calls == []
        assert mocks['find_host_id'].mock_calls == []
        assert mocks['discover_engine'].mock_calls == []
        assert mocks['discover_sensors'].mock_calls == []
        assert mock_list.call_count == 1

    def test_init_nondefault(self):
        dummy = Mock()
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                find_host_id=DEFAULT,
                discover_engine=DEFAULT,
                discover_sensors=DEFAULT,
                list_classes=DEFAULT,
            ) as mocks:
                mocks['find_host_id'].return_value = 'myhostid'
                mocks['discover_engine'].return_value = ('foo.bar.baz', 1234)
                mocks['discover_sensors'].return_value = [dummy]
                cls = SensorDaemon(
                    dry_run=True,
                    dummy_data=True,
                    engine_port=1234,
                    engine_addr='foo.bar.baz',
                    interval=12.34,
                    class_args={'foo': 'bar'}
                )
        assert cls.dry_run is True
        assert cls.dummy_data is True
        assert cls.engine_port == 1234
        assert cls.engine_addr == 'foo.bar.baz'
        assert cls.interval == 12.34
        assert cls.host_id == 'myhostid'
        assert cls.sensors == [dummy]
        assert mock_logger.mock_calls == [
            call.warning('This machine running with host_id %s', 'myhostid'),
            call.warning("DRY RUN MODE - will not POST data to Engine.")
        ]
        assert mocks['find_host_id'].mock_calls == [call(cls)]
        assert mocks['discover_engine'].mock_calls == []
        assert mocks['discover_sensors'].mock_calls == [
            call(cls, {'foo': 'bar'})
        ]
        assert mocks['list_classes'].mock_calls == []

    def test_init_no_sensors(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch.multiple(
                pb,
                autospec=True,
                find_host_id=DEFAULT,
                discover_engine=DEFAULT,
                discover_sensors=DEFAULT,
                list_classes=DEFAULT,
            ) as mocks:
                mocks['find_host_id'].return_value = 'myhostid'
                mocks['discover_engine'].return_value = ('foo.bar.baz', 1234)
                with pytest.raises(SystemExit) as excinfo:
                    SensorDaemon()
        assert mock_logger.mock_calls == [
            call.warning('This machine running with host_id %s', 'myhostid'),
            call.critical('ERROR - no sensors discovered.')
        ]
        assert mocks['find_host_id'].call_count == 1
        assert mocks['discover_engine'].call_count == 1
        assert mocks['discover_sensors'].call_count == 1
        assert excinfo.value.code == 1
        assert mocks['list_classes'].mock_calls == []

    def test_run(self):
        def se_ras(klass):
            if mock_ras.call_count < 4:
                return None
            raise RuntimeError()

        with patch('%s.read_and_send' % pb, autospec=True) as mock_ras:
            with patch('%s.sleep' % pbm, autospec=True) as mock_sleep:
                with patch('%s.logger' % pbm, autospec=True) as mock_logger:
                    mock_ras.side_effect = se_ras
                    with pytest.raises(RuntimeError):
                        self.cls.run()
        assert mock_ras.mock_calls == [
            call(self.cls),
            call(self.cls),
            call(self.cls),
            call(self.cls)
        ]
        assert mock_sleep.mock_calls == [
            call(60.0),
            call(60.0),
            call(60.0)
        ]
        assert mock_logger.mock_calls == [
            call.info('Running sensor daemon loop...'),
            call.debug('Sleeping %ss', 60.0),
            call.debug('Sleeping %ss', 60.0),
            call.debug('Sleeping %ss', 60.0)
        ]

    def test_sensor_classes(self):

        class EP1(object):
            name = 'EP1'

        class EP2(object):
            name = 'EP2'

        with patch('%s.load_classes' % pbm, autospec=True) as mock_load:
            with patch('%s.logger' % pbm, autospec=True) as mock_logger:
                mock_load.return_value = [EP1, EP2]
                res = self.cls._sensor_classes()
        assert res == [EP1, EP2]
        assert mock_load.mock_calls == [
            call('rpymostat.sensors', superclass=BaseSensor)
        ]
        assert mock_logger.mock_calls == [
            call.debug("%s Sensor classes loaded successfully: %s",
                       2, ['EP1', 'EP2'])
        ]

    def test_discover_sensors(self):

        class Class1(object):

            def sensors_present(self):
                pass

        class Class2(object):

            def sensors_present(self):
                pass

        class Class3(object):

            def sensors_present(self):
                pass

        class Class4(object):

            def sensors_present(self):
                pass

        def se_exc(s):
            raise RuntimeError()

        mock_cls1 = Mock(spec=Class1)
        mock_cls1.sensors_present.return_value = True
        mock1 = Mock(spec=Class1)
        mock1.return_value = mock_cls1

        mock_cls2 = Mock(spec=Class2)
        mock_cls2.sensors_present.return_value = False
        mock2 = Mock(spec=Class2)
        mock2.return_value = mock_cls2

        mock_cls3 = Mock(spec=Class3)
        mock_cls3.sensors_present.side_effect = se_exc
        mock3 = Mock(spec=Class3)
        mock3.return_value = mock_cls3

        mock4 = Mock(spec=Class4)
        mock4.side_effect = se_exc

        classes = [mock1, mock2, mock3, mock4]

        cls_args = {'Class1': {'foo': 'bar'}}

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s._sensor_classes' % pb) as m_classes:
                m_classes.return_value = classes
                res = self.cls.discover_sensors(class_args=cls_args)
        assert res == [mock_cls1]
        assert m_classes.mock_calls == [call()]
        assert mock_cls1.mock_calls == [call.sensors_present()]
        assert mock1.mock_calls == [
            call(foo='bar'),
            call().sensors_present()
        ]
        assert mock_logger.mock_calls == [
            call.debug('Checking sensor classes for sensors...'),
            call.info('Sensor class %s.%s reports sensors present',
                      'rpymostat_sensor.tests.test_sensor_daemon', 'Class1'),
            call.debug('Exception while discovering sensors via %s.%s',
                       'rpymostat_sensor.tests.test_sensor_daemon',
                       'Class3', exc_info=1),
            call.debug('Exception while instantiating sensor class %s with '
                       'kwargs=%s', 'Class4', {}, exc_info=1),
            call.debug('Discovered %d sensor classes with sensors present', 1)
        ]

    def test_discover_sensors_dummy(self):
        self.cls.dummy_data = True

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s._sensor_classes' % pb) as m_classes:
                res = self.cls.discover_sensors()
        assert m_classes.mock_calls == []
        assert len(res) == 1
        assert isinstance(res[0], DummySensor)
        assert res[0].host_id == 'myhostid'
        assert mock_logger.mock_calls == [
            call.warning('Running with --dummy - only DummySensor() will be '
                         'loaded')
        ]

    def test_read_and_send(self):

        def se_exc():
            raise Exception()

        s1 = Mock(spec_set=BaseSensor)
        s1.read.return_value = {
            'sensor1': {'data': 's1data'},
            'sensor2': {'data': 's2data'},
        }

        s2 = Mock(spec_set=BaseSensor)
        s2.read.side_effect = se_exc

        s3 = Mock(spec_set=BaseSensor)
        s3.read.return_value = {
            'sensor31': {'data': 's31data'},
            'sensor32': {'data': 's32data'},
        }

        self.cls.sensors = [s1, s2, s3]

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.requests.post' % pbm, autospec=True) as mock_post:
                mock_post.return_value = Mock(status_code=201)
                self.cls.read_and_send()
        url = 'http://foo.bar.baz:1234/v1/sensors/update'
        data = {
             'host_id': 'myhostid',
             'sensors': {
                 'sensor1': {'data': 's1data'},
                 'sensor2': {'data': 's2data'},
                 'sensor31': {'data': 's31data'},
                 'sensor32': {'data': 's32data'},
             }
         }
        assert mock_post.mock_calls == [
            call(url, json=data)
        ]
        assert mock_logger.mock_calls == [
            call.debug('Reading sensors'),
            call.exception('Exception reading sensor %s', 'BaseSensor'),
            call.debug('POSTing sensor data to %s: %s', url, data),
            call.info('POSTed sensor data to Engine')
        ]

    def test_read_and_send_bad_status_code(self):
        s1 = Mock(spec_set=BaseSensor)
        s1.read.return_value = {
            'sensor1': {'data': 's1data'},
            'sensor2': {'data': 's2data'},
        }

        self.cls.sensors = [s1]

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.requests.post' % pbm, autospec=True) as mock_post:
                mock_post.return_value = Mock(status_code=404, text='foo')
                self.cls.read_and_send()
        url = 'http://foo.bar.baz:1234/v1/sensors/update'
        data = {
             'host_id': 'myhostid',
             'sensors': {
                 'sensor1': {'data': 's1data'},
                 'sensor2': {'data': 's2data'}
             }
         }
        assert mock_post.mock_calls == [
            call(url, json=data)
        ]
        assert mock_logger.mock_calls == [
            call.debug('Reading sensors'),
            call.debug('POSTing sensor data to %s: %s', url, data),
            call.error('Error POSTing sensor data; got status code %s: %s',
                       404, 'foo')
        ]

    def test_read_and_send_exception(self):

        def se_exc(*args, **kwargs):
            raise Exception()

        s1 = Mock(spec_set=BaseSensor)
        s1.read.return_value = {
            'sensor1': {'data': 's1data'},
            'sensor2': {'data': 's2data'},
        }

        self.cls.sensors = [s1]

        with patch('%s.logger' % pbm, autospec=True) as mock_logger:
            with patch('%s.requests.post' % pbm, autospec=True) as mock_post:
                mock_post.side_effect = se_exc
                self.cls.read_and_send()
        url = 'http://foo.bar.baz:1234/v1/sensors/update'
        data = {
             'host_id': 'myhostid',
             'sensors': {
                 'sensor1': {'data': 's1data'},
                 'sensor2': {'data': 's2data'}
             }
         }
        assert mock_post.mock_calls == [
            call(url, json=data)
        ]
        assert mock_logger.mock_calls == [
            call.debug('Reading sensors'),
            call.debug('POSTing sensor data to %s: %s', url, data),
            call.exception('Exception caught when trying to POST data to '
                           'Engine; will try again at next interval.')
        ]

    def test_find_host_id(self):
        with patch('%s.SystemID.id_string' % pbm,
                   new_callable=PropertyMock) as mock_sys_id:
            mock_sys_id.return_value = 'utilsHostId'
            res = self.cls.find_host_id()
        assert res == 'utilsHostId'
        assert mock_sys_id.mock_calls == [call()]

    def test_discover_engine(self):
        with patch('%s.utils_discover_engine' % pbm, autospec=True) as mock_de:
            with patch('%s.logger' % pbm, autospec=True) as mock_logger:
                mock_de.return_value = ('engine_addr', 1234)
                res = self.cls.discover_engine()
        assert res == ('engine_addr', 1234)
        assert mock_de.mock_calls == [call()]
        assert mock_logger.mock_calls == [
            call.info('Discovered Engine at %s:%s', 'engine_addr', 1234)
        ]

    def test_get_varnames(self):
        docstr = {
            'params': {
                'argOne': 'arg one info',
                'argTwo': 'arg two info is a long line',
                'kwarg1': 'kwarg1 info',
            },
            'types': {
                'argOne': 'str',
                'argTwo': 'int',
                'kwarg1': 'str'
            }
        }
        ds = """
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
        with patch('%s._parse_docstring' % pb) as mock_pd:
            mock_pd.return_value = docstr
            res = self.cls._get_varnames(TestSensor)
        assert mock_pd.mock_calls == [call(ds)]
        assert res == {
            'argOne': '(str) arg one info',
            'argTwo': '(int) arg two info is a long line',
            'kwarg1=None': '(str) kwarg1 info',
            'kwarg2=1234': ''
        }

    def test_get_varnames_kwargs_only(self):

        class Foo(object):

            def __init__(self, foo=1, bar='two'):
                """mystr"""
                pass

        docstr = {
            'params': {
                'foo': 'arg one info',
                'bar': 'arg two info is a long line',
            },
            'types': {
                'foo': 'str',
            }
        }
        with patch('%s._parse_docstring' % pb) as mock_pd:
            mock_pd.return_value = docstr
            res = self.cls._get_varnames(Foo)
        assert mock_pd.mock_calls == [call('mystr')]
        assert res == {
            'foo=1': '(str) arg one info',
            'bar=two': 'arg two info is a long line'
        }

    def test_get_varnames_no_default(self):

        class Foo(object):

            def __init__(self, arg1, arg2):
                """foo"""
                pass

        docstr = {
            'params': {
                'arg1': 'arg one info'
            },
            'types': {
                'arg1': 'str'
            }
        }
        with patch('%s._parse_docstring' % pb) as mock_pd:
            mock_pd.return_value = docstr
            res = self.cls._get_varnames(Foo)
        assert mock_pd.mock_calls == [call("foo")]
        assert res == {
            'arg1': '(str) arg one info',
            'arg2': '',
        }

    def test_parse_docstring(self):
        docstring = """
        Some text here
        About the init function

        Foo

        Bar.

        :param argOne: arg one info
        :type argOne: str
        :param argTwo: arg two info is a
          long
          line
        :type argTwo: int
        :param kwarg1: kwarg1 info
        :type kwarg1: str
        :param kwarg2: kwarg2 info
        :return: foo
        """
        res = self.cls._parse_docstring(docstring)
        assert res == {
            'params': {
                'argOne': 'arg one info',
                'argTwo': 'arg two info is a long line',
                'kwarg1': 'kwarg1 info',
                'kwarg2': 'kwarg2 info'
            },
            'types': {
                'argOne': 'str',
                'argTwo': 'int',
                'kwarg1': 'str'
            }
        }

    def test_list_classes(self, capsys):
        varnames_one = {
            'argOne': '(int) arg one info',
            'argTwo': 'arg two info',
            'kwarg1=foo': '(str) kwarg1 info'
        }

        m1 = MagicMock(__name__='clsone', _description='desc1')
        m2 = MagicMock(__name__='cls2', _description='desc2')

        def se_gv(klass):
            if klass == m1:
                return varnames_one
            return {}

        with patch('%s._sensor_classes' % pb) as mock_classes:
            with patch('%s._get_varnames' % pb) as mock_gv:
                mock_classes.return_value = [m1, m2]
                mock_gv.side_effect = se_gv
                SensorDaemon.list_classes()
        assert mock_classes.mock_calls == [call()]
        assert mock_gv.mock_calls == [call(m1), call(m2)]
        expected_out = "Discovered Sensor Classes:\n\n"
        expected_out += "clsone (desc1)\n"
        expected_out += "    argOne - (int) arg one info\n"
        expected_out += "    argTwo - arg two info\n"
        expected_out += "    kwarg1=foo - (str) kwarg1 info\n"
        expected_out += "\n"
        expected_out += "cls2 (desc2)\n\n"
        out, err = capsys.readouterr()
        assert err == ''
        assert out == expected_out
