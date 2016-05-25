# prometheus-mumble
A simple interface to gather statistics from mumble

## Install
You can run this in a virtual env or build with pants.

```
 $ pants binary src:mumble-prometheus
 $ dist/mumble-prometheus.pex --host 127.0.0.1 --port 6502 --listen 9123 --secret=ice_secret
```
