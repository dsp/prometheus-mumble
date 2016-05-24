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

    g = node.Gauge('users_connected', 'Number of connected users')
    while True:
        t1 = time.time()
        print('gathering statistics')
        with ice_connect(args.host, args.port) as meta:
            for server in meta.getBootedServers():
                g.set(len(server.getUsers()))
        time_to_wait = args.interval - (time.time() - t1)
        if time_to_wait > 0:
            time.sleep(time_to_wait)
    return 0

if __name__ == '__main__':
    sys.exit(main())

