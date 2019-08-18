import time
from argparse import ArgumentParser
from functools import partial
from http.server import ThreadingHTTPServer

from handler import GeoCoderHTTPRequestHandler

if __name__ == '__main__':
    parser = ArgumentParser(description='Start a GeoCoder HTTP server on localhost.')
    parser.add_argument("-p", "--port", type=int, default=4321)
    parser.add_argument("-g", "--google-key")
    parser.add_argument("-b", "--bing-key")

    args = parser.parse_args()
    httpd = ThreadingHTTPServer(("localhost", args.port),
                                partial(GeoCoderHTTPRequestHandler,
                                        args.google_key,
                                        args.bing_key))

    print("{} Listening on localhost:{}".format(time.asctime(), args.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Bye bye!")
