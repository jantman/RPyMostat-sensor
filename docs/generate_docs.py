#!/usr/bin/env python

import os
from rpymostat_sensor.sensor_daemon import SensorDaemon

doc_path = os.path.join(os.path.dirname(__file__), 'source')

# read the template
with open(os.path.join(doc_path, 'sensor_support.rst.template'), 'r') as fh:
    tmpl_content = fh.read()
result = tmpl_content

# build the sensor_support docs
sensor_classes = SensorDaemon._sensor_classes()
s = ''
for cls in sorted(sensor_classes):
    desc = ''
    if hasattr(cls, '_description'):
        desc = cls._description
    s += '* :py:class:`~%s.%s` (%s)' % (cls.__module__, cls.__name__, desc)

result = result.replace('<<SENSORS HERE>>', s)

# write the file
with open(os.path.join(doc_path, 'sensor_support.rst'), 'w') as fh:
    fh.write(result)