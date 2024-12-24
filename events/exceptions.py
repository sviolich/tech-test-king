class ServiceException(Exception):
    def __init__(self, message, inner_exception=None):
        super().__init__(message)
        self.inner_exception = inner_exception

    def __str__(self):
        if self.inner_exception:
            return f"{super().__str__()} (caused by: {str(self.inner_exception)})"
        return super().__str__()
