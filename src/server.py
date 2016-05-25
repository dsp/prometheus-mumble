from __future__ import print_function

import sys

import prometheus_client as node
from contextlib import contextmanager

import argparse, time, logging
import Ice, Murmur

logger = logging.getLogger('mumble-prometheus')

@contextmanager
def ice_connect(host, port, secret=None):
    prxstr = "Meta:tcp -h %s -p %d -t 1000" % (host, port)

    props = Ice.createProperties(sys.argv)
    props.setProperty("Ice.ImplicitContext", "Shared")
    props.setProperty('Ice.Default.EncodingVersion', '1.0')

    idata = Ice.InitializationData()
    idata.properties = props

    ic = Ice.initialize(idata)
    if secret:
        ic.getImplicitContext().put("secret", secret)

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
    parser.add_argument('--secret', help='The read secret', default=None)
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    args = parser.parse_args()

    node.start_http_server(args.listen)

    gauges = {
        'users': node.Gauge('mumble_users_connected', 'Number of connected users',
            ['ice_server', 'server_id']),
        'uptime': node.Gauge('mumble_uptime', 'Virtual uptime',
            ['ice_server', 'server_id']),
    }

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ice_server = '%s:%d' % (args.host, args.port)
    with ice_connect(args.host, args.port, args.secret) as meta:
        while True:
            logger.info('gathering info')
            t1 = time.time()
            for server in meta.getBootedServers():
                g_user = len(server.getUsers())
                g_uptime = server.getUptime()
                logger.debug('mumble_user_connected: %d' % g_user)
                logger.debug('mumble_uptime: %d' % g_uptime)
                labels = {'server_id': server.id(), 'ice_server': ice_server}
                gauges['users'].labels(labels).set(g_user)
                gauges['uptime'].labels(labels).set(g_uptime)

            time_to_wait = args.interval - (time.time() - t1)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
    return 0

if __name__ == '__main__':
    sys.exit(main())

