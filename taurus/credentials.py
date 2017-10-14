rom ConfigParser import ConfigParser, RawConfigParser
from sclutils import logger as scllog
import os

__all__ = ['Credentials']

AUTH = {
    'etoro':
        {'api': [
            'app_id',
            'app_secret',
            'long_access_token'
        ]}
}

DEFAULT_PROFILE = {
    'etoro': 'api',
}

class Credentials(object):
    """ Class to manager authentication
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
    configure
        Create credential files for the given service.
    load
        Load paramters from credential files.
    create_config_file
        Create configureation file
    """

    def __init__(self, service, credentials_folder='.credentials',
        credentials_filename=None):

        self._service = service
        self._home = os.path.expanduser("~")
        self._credential_dir = os.path.join(self._home, credentials_folder)
        if credentials_filename is None:
            credentials_filename = '{}'.format(service)

        self._config_file = os.path.join(self._credential_dir,
                                         credentials_filename)
        self.credentials = {}
        if not os.path.isdir(self._credential_dir):
            os.mkdir(self._credential_dir)

    def __getattr__(self, item):
        if item in self.credentials.keys():
            return self.credentials[item]

    def __str__(self):
        return "\n".join( ["{}: {}".format(k, v) \
                           for k, v in self.credentials.items()] )

    @property
    def name(self):
        return self._service

    def config_exists(self):
        return os.path.isfile(self._config_file)

    def create_config_file(self, params):
        """ Create configuration file
        Parameters
        ----------
        params: dict
            Dictionary or reguired paramters.
        """

        LOG.info("Creating config file in {}".format(self._credential_dir))
        config = RawConfigParser()
        config.add_section(DEFAULT_PROFILE[self._service])

        for k, v in params.items():
            config.set(DEFAULT_PROFILE[self._service], k, v)

        with open(self._config_file, 'wb') as file:
            config.write(file)

    def load(self):
        """ Load configuration file. """

        config = ConfigParser()
        config.read(self._config_file)

        for k, v in config.items(DEFAULT_PROFILE[self._service]):
            self.credentials[k] = v

    def configure(self, params=None):
        """ Configure and save API credentials."""

        if self.config_exists():
            LOG.warning("A config files was found. Press 0 to proceed.")

            if raw_input('Press ') != '0':
                LOG.warning("Aborting configuration.")
                return None

        if params is None:
            params = {}
            for k in AUTH[self._service][DEFAULT_PROFILE[self._service]]:
                params[k] = raw_input("Enter {}: "\
                                      .format(' '.join(k.split('_'))))

        self.create_config_file(params)

    def add(self, value_dict):
        for k, v in value_dict.items():
            self.credentials[k] = v