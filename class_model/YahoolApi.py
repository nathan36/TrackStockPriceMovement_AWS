import requests
import json
from dataclasses import dataclass

@dataclass
class config:
    symbols: str
    api_key: str


class yahool_api:

    def __init__(self, api_key):
        self.key = api_key

    def run(self, symbols):
        try:
            url = "https://rest.yahoofinanceapi.com/v6/finance/quote"
            querystring = {"symbols": symbols}
            headers = {'x-api-key': self.key}
            response = requests.request("GET", url, headers=headers,
                                        params=querystring)
            if response.status_code == 200:
                result = json.loads(response.text)
                return {'response':result['quoteResponse'],
                        'status':response.status_code}
            else:
                return {'status':response.status_code}
        except:
            raise



