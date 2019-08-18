# GeoCoder

A simple HTTP server which takes in a JSON address payload via POST and
returns the lat/long coordinates of the address, along with a confidence
of accuracy.

Since the server only does one thing, all traffic is served from the server
root without any request routing based on the path.

Uses Google Maps to do the geocoding, and falls back to Bing Maps if Google
either fails or returns no results

## Run

```shell
py server.py [-p|--port PORT] -g|--google-key GOOGLE_API_KEY -b|--bing-key BING_API_KEY
```

`PORT` defaults to `4321` if unspecified

When done, simply `Ctrl+C` to shutdown the server

## Input

JSON Schema specification:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "line": { "type": "string" },
    "city": { "type": "string" },
    "state": { "type": "string" },
    "postal": { "type": "string" },
    "country": { "type": "string" }
  },
  "required": [ "line" ],
  "oneOf": [
    { "required": [ "city", "state" ] },
    { "required": [ "postal" ] }
  ]
}
```

Example 1:
```
POST /

{
  "line": "123 Main St",
  "postal": "V6A2S5",
  "country": "CA" 
}
```

Example 2:
```
POST /

{
  "line": "123 Main St",
  "city": "San Francisco",
  "state": "CA"
}
```

## Output

If the address geocodes successfully:

```
200 OK

{
  "lat": 37.791758,
  "long": -122.394341,
  "confidence": "High"
}
```

where `confidence` is one of `"High"`, `"Medium"`, or `"Low"`

All non-`200` responses consist of a JSON response payload with an `error`
message field containing a human-readable error string.

If the address can't be geocoded, a `404` is returned with an appropriate
JSON error response payload