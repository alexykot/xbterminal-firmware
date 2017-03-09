class NetworkError(Exception):
    pass


class ServerError(Exception):

    def contains(self, message):
        """
        Look for specific message in error data
        """
        if not self.args or not isinstance(self.args[0], dict):
            return False
        for key, messages in self.args[0].items():
            if message in messages:
                return True
        return False


class OrderNotFound(Exception):
    pass


class StageTimeout(Exception):
    pass
