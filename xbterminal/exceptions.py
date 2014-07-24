class XBTerminalError(Exception):

    strerror = 'error'

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.strerror)


class NetworkError(XBTerminalError):
    strerror = 'network error'


class ConfigLoadError(XBTerminalError):
    strerror = 'configuration load failure'


class DeviceKeyMissingError(XBTerminalError):
    strerror = 'device key missing'
