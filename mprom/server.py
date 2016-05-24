from __future__ import print_function

import sys

import prometheus_client as node
from contextlib import contextmanager

import argparse, time
import Ice, Murmur


@contextmanager
def ice_connect(host, port):
    prxstr = "Meta:tcp -h %s -p %d -t 1000" % (host, port)

    ic = Ice.initialize(sys.argv)
    base = ic.stringToProxy(prxstr)
    meta = Murmur.MetaPrx.checkedCast(base)
    if not meta:
        print('cannot establish connection', file=sys.stderr)
        sys.exit(1)

    yield meta

    if ic:
        ic.destroy()


def main():
    parser = argparse.ArgumentParser(description='Prometheus statistics for a Mumble ICE interface')
    parser.add_argument('-l', '--listen', help='Port to listen on', default=9123, type=int)
    parser.add_argument('-H', '--host', help='Host of the Ice interface', default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port of the Ice interface', default=6502, type=int)
    parser.add_argument('-i', '--interval', help='Interval in seconds', default=60, type=int)
    args = parser.parse_args()

    node.start_http_server(args.listen)

    gauges = {
        'users': node.Gauge('mumble_users_connected', 'Number of connected users',
            ['ice_server', 'server_id']),
        'uptime': node.Gauge('mumble_uptime', 'Virtual uptime',
            ['ice_server', 'server_id']),
    }

    ice_server = '%s:%d' % (ags.host, args.port)
    while True:
        t1 = time.time()
        with ice_connect(args.host, args.port) as meta:
            for server in meta.getBootedServers():
                labels = {'server_id': server.id(), 'ice_server': ice_server}
                gauges['users'].labels(labels).set(len(server.getUsers()))
                gauges['uptime'].labels(labels).set(server.getUptime())

        time_to_wait = args.interval - (time.time() - t1)
        if time_to_wait > 0:
            time.sleep(time_to_wait)
    return 0

if __name__ == '__main__':
    sys.exit(main())

