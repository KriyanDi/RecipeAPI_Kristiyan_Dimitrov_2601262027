class AppError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NotFound(AppError):
    pass

class DublicationError(AppError):
    pass

class ConflictError(AppError):
    pass
