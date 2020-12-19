from dataclasses import dataclass


@dataclass
class RabbitMQConnectionParameters:
    host: str
    port: int = 5672
