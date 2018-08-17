from datetime import timedelta
from datetime import datetime as dt
import requests
import threading
import json
import collections


SOLAREDGE_URL = 'https://monitoringapi.solaredge.com/site/{0}/overview?api_key={1}'
HTTP_GET = 'GET'
ERROR_RESPONSE = 'error_response'

def build_url(api_key, site_id):
    """
        This function builds the request url
        API details https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf

        key:        Your Solar Edge Key
        site_id:    The ID of a Site
    
    """
   
    
    baseURL = requests.Request(HTTP_GET, SOLAREDGE_URL.format(site_id,api_key)).prepare().url
    return baseURL


def get_se(requestURL):
    """Get Solar Edge API response."""
    se_response = requests.get(requestURL)
    se_response.raise_for_status()

    json_d = se_response.json()
    headers = se_response.headers

    if ERROR_RESPONSE in json_d:
        code = json_d.get(ERROR_RESPONSE).get('code')
        msg = json_d.get(ERROR_RESPONSE).get('error_msg')
        raise Exception('API returned error code {}. {}'.format(code, msg))

    return PowerDataPoint(json_d['overview'], headers, se_response)
   


class SE_Forecast():

    def __init__(self, api_key, site_id):
        self.api_key = api_key
        self.site_id = site_id
       
    def get_current(self):
        """Get current forecast."""

        url = build_url(self.api_key, self.site_id)
        return get_se(url)


class PowerDataPoint():

    def __init__(self, d={}, headers=None, response=None):
        self.d = d
        self.headers = headers
        self.response = response
        self.Daily = d['lastDayData']['energy']
        self.Lifetime = d['lifeTimeData']['energy']
        self.Current = d['currentPower']['power']
        self.Month = d['lastMonthData']['energy']
        self.LastUpdate = d['lastUpdateTime']

    

 

class PropertyUnavailable(AttributeError):
    """Raise when an attribute is not available for a forecast."""
