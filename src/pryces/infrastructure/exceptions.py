class ConfigurationError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Configuration error: {reason}")
