import requests
import os
import datetime
from ..credentials import *
from datetime import datetime
import types

__all__ = ['Etoro']

DATE_FORMAT = "%Y-%m-%d"

def add_url(base_url, params):
    if params is not None:
        flag = '&' if '?' in base_url else '?'
        base_url += flag
        for k,v in params.items():
            base_url += '{}={}'.format(k,v)

    return base_url

class Etoro(object):
    """ Wrapper for Etoro API
    Parameters
    ----------
    service: str
        Which service credential to handle
    Attributes
    ----------
    name: str
        Service name handled.
    _home: str
        Absolute path for user.
    _credential_dir: str
        Absolute path of credential directory for the service.
    _config_file: str
        Absolute path of credential file for the service.
    Methods
    -------
    connect
        Create credential files for the given service.
    get
        Do GET request to api url.
    post
        Do POST request to api url.
    """
    def __init__(self):

        self.credentials = Credentials('etoro')
        self.location = None
        self.connect()

    def __getattr__(self, item):

        if hasattr(self.credentials, item):
            return getattr(self.credentials, item)

    def _authenticate(self):

        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.api_key),
        }
        response = requests.post(self.authentication_url, header=headers)
        grantLocation = response.headers['location']
        return grantLocation

    def _get_service_ticket(self, service):

        payload = {'service': service}
        serviceTicket = requests.post(self.location,
                                      data=payload).text
        return serviceTicket

    def connect(self):
        """ Connect to Lotame API using credentials in ~/.lotame/config."""

        LOG.info("Connecting to Lotame API.")

        if self.config_exists():
            self.load()
        else:
            raise ValueError("Cannot load config file, it does not exist, "
                             "please create one.")

        self.location = self._get_granting_location()

    def get(self, endpoint, params=None):
        """Do a GET request to Etoro API for a specific service.
        Parameters
        ----------
        service: str
            Service url for GET request.
        """

        url = self.api_url + endpoint
        url = add_url(url, params)

        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.api_key),
        }
        response = requests.get(
            url,
            headers=headers,
        )

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            LOG.error(err)

    def delete(self, endpoint, params=None):
        """Do a DELETE request to Etoro API.
        Parameters
        ----------
        service: str
            Service url for GET request.
        """

        url = self.api_url + endpoint
        url = add_url(url, params)

        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.api_key),
        }
        response = requests.get(
            url,
            headers=headers,
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            LOG.error(err)

    def post(self, service, payload):
        """ Do a POST request to Etoro API.
        Parameters
        ----------
        service: str
            Service url for GET request.
        payload: str
            Parameter for POST request.
        """

        url = self.api_url + service
        url = add_url(url, payload)

        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.api_key),
        }

        response = requests.post(
            url,
            headers = headers,
            data = payload
        )
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            LOG.error(err)


class JsonWrap:

    methods = ['to_dict', 'methods']

    def __init__(self, entries):
        self.__dict__.update(entries)
        for k,v in self.__dict__.items():
            if type(v) == types.DictType:
                setattr(self, k, JsonWrap(**v))

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()


class Behavior(JsonWrap):

    def __or__(self, other):
        out = {}
        out['components'] = []
        out['components'].append({'complexAudienceBehavior': self})
        out['components'].append({'complexAudienceBehavior': other,
                                 'operator': 'OR'})
        return Behavior(out)
