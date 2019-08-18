import json
from functools import partial
from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode


class GeoCoderHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, google_key, bing_key, *args, **kwargs):
        self.google_key = google_key
        self.bing_key = bing_key
        super().__init__(*args, **kwargs)

    def do_POST(self):
        address = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if not GeoCoderHTTPRequestHandler.is_valid(address):
            self.write_response(400, {"error": "Address line and either city+state or postal must be specified"})
            return

        (code, resp) = self.geocode_with_google(address)
        if code != 200:
            (code, resp) = self.geocode_with_bing(address)

        self.write_response(code, resp)

    def geocode_with_google(self, address):
        try:
            address_parts = [address["line"], address["city"], address["state"], address["postal"]]
            address_param = ", ".join([ap for ap in address_parts if not ap.isspace()])

            connection = HTTPSConnection("maps.googleapis.com")
            connection.request("GET", "/maps/api/geocode/json?{}".format(urlencode({"address": address_param,
                                                                                    "key": self.google_key})))
            response = connection.getresponse()
            result = json.loads(bytes.decode(response.read(), 'utf-8'))
            if result["status"] == "OK":
                geo = result["results"][0]["geometry"]
                location = geo["location"]
                lt = geo["location_type"]
                confidence = "High" if lt == "ROOFTOP" else "Low" if lt == "APPROXIMATE" else "Medium"
                return 200, {"lat": location["lat"],
                             "long": location["lng"],
                             "confidence": confidence}
            else:
                return 404 if result["status"] == "ZERO_RESULTS" else 500,\
                       {"error": "Google couldn't find anything: " + result["status"]}
        except Exception as e:
            return 500, {"error": "Error encountered with Google: " + str(e)}

    def geocode_with_bing(self, address):
        try:
            bing_address = {"adminDistrict": address.get("state", ""),
                            "postalCode": address.get("postal", ""),
                            "locality": address.get("city", ""),
                            "addressLine": address["line"],
                            "countryRegion": "US",  # only support US for now
                            "key": self.bing_key}
            bing_address = {k: v for k, v in bing_address.items() if not v.isspace()}

            connection = HTTPSConnection("dev.virtualearth.net")
            connection.request("GET", "/REST/v1/Locations?{}".format(urlencode(bing_address)),
                               headers={"Content-Type": "application/json"})

            response = connection.getresponse()
            result = json.loads(bytes.decode(response.read(), 'utf-8'))
            status = result["statusCode"]
            if status == 200 and len(result["resourceSets"]) > 0 and len(result["resourceSets"][0]["resources"]) > 0:
                location = result["resourceSets"][0]["resources"][0]
                coords = location["point"]["coordinates"]
                return 200, {"lat": coords[0], "long": coords[1], "confidence": location["confidence"]}
            else:
                return 404 if status == 200 else status,\
                       {"error": "Bing couldn't find anything: " + result["statusDescription"],
                        "errorDetails": result.get("errorDetails", [])}
        except Exception as e:
            return 500, {"error": "Error encountered with Bing: " + str(e)}

    def write_response(self, code, data):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    @staticmethod
    def is_valid(address):
        v = partial(GeoCoderHTTPRequestHandler.has_valid_key, address)
        return v("line") and (v("postal") or (v("city") and v("state")))

    @staticmethod
    def has_valid_key(address, key):
        return key in address and not address[key].isspace()
