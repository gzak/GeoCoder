import json
import time
from argparse import ArgumentParser
from functools import partial
from http.client import HTTPSConnection
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class GeoCoderHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, google_key, bing_key, *args, **kwargs):
        self.google_key = google_key
        self.bing_key = bing_key
        super().__init__(*args, **kwargs)

    def do_POST(self):
        connection1 = HTTPSConnection("maps.googleapis.com")
        connection1.request("GET", "/maps/api/geocode/json?address=1247+Lakeside+Dr,+Sunnyvale,+CA+94085&key=" + self.google_key)
        response = connection1.getresponse()
        self.send_response(200)
        self.end_headers()
        text = bytes.decode(response.read(), 'utf-8')
        data = json.loads(text)
        print(json.dumps(data, indent=4, sort_keys=True))
        self.wfile.write('{{"lat": {}, "long":{}}}'.format(data["results"][0]["geometry"]["location"]["lat"], data["results"][0]["geometry"]["location"]["lng"]).encode("utf-8"))


if __name__ == '__main__':
    parser = ArgumentParser(description='Start a GeoCoder HTTP server on localhost.')
    parser.add_argument("-p", "--port", type=int, default=4321)
    parser.add_argument("-gk", "--google-key")
    parser.add_argument("-bk", "--bing-key")

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
