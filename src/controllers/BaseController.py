from helpers.config import get_settings, Settings

class BaseController:
    """
    Base controller for handling common operations.
    """

    def __init__(self):
        self.app_settings = get_settings()