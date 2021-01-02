from dataclasses import dataclass


@dataclass
class DatabaseConnectionParameters:
    host: str
    database: str
    username: str
    password: str
    port: int = 5432
