# vim: syntax=python:expandtab:shiftwidth=2:softtabstop=2:tabstop=2
python_binary(
  name='mumble-prometheus',
  dependencies=[
    ':murmur',
    ':ext-deps',
  ],
  source='server.py',
)
python_library(
  name='murmur',
  sources=['Murmur.py', 'Murmur_ice.py'],
)
python_requirement_library(
  name='ext-deps',
  requirements=[
      python_requirement('prometheus-client>=0.0.13'),
      python_requirement('zeroc-ice>=3.6.2.1'),
  ]
)
