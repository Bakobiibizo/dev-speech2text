import os
from loguru import logger
from utilities.data_models import (
    EndpointConfig,
    ConfigManager,
    EndpointLabels,
    EndpointMap,
)
from dotenv import load_dotenv

load_dotenv()


class EndpointConfigManager(ConfigManager):
    def __init__(self):
        super().__init__()
        self.environment = os.getenv("environment")
        self.version = os.getenv("version")
        self.endpoint_map = EndpointMap().dict()
        self.endpoint_label = EndpointLabels().dict()
        self.url_map = {}
        self.speech2text = self.get_config("speech2text")
        self.all_config = self.set_all_config()

    def _set_config(self, labels) -> None:
        for key, value in labels.items():
            self.__setattr__(key, self.get_config(value))

    def set_all_config(self):
        self.all_config = {}
        for key, value in self.endpoint_map.items():
            self.url_map[key] = (
                f"http://{self.speech2text.host}:{self.speech2text.port}{self.version}{value}"
            )
        for key, value in os.environ.items():
            self.all_config[key] = value
            return self.all_config

    def get_map_endpoint(self, endpoint):
        return self.endpoint_map[endpoint]

    def get_url(self, host, port, endpoint):
        return f"http://{host}:{port}{endpoint}"

    def get_config(self, value: str):
        host = handle_error(os.getenv(f"{self.environment}_{value}_host"), value)
        port = handle_error(os.getenv(f"{self.environment}_{value}_port"), value)
        endpoint = handle_error(
            os.getenv(f"{self.environment}_{value}_endpoint"), value
        )

        config_map = {"host": host, "port": port, "endpoint": endpoint}

        config_map["url"] = self.get_url(**config_map)
        return EndpointConfig(**config_map)

    def set_item(self, key, value):
        value = os.getenv(f"{self.environment}_{value}")
        self.__setattr__(key, value)


def handle_error(input, value):
    if input is None:
        raise ValueError(f"value cannot be None:\n {value}")
    else:
        return input


def getEndpointConfigManager():
    config_manager = EndpointConfigManager()
    return config_manager


def main():
    return getEndpointConfigManager()


if __name__ == "__main__":
    manager = main()
