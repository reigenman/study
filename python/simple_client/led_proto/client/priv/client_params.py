from dataclasses import dataclass


@dataclass(frozen=True)
class ClientParams:
    host: str
    port: int

    def __post_init__(self):
        if not self.host:
            raise ValueError('host is invalid')
        if self.port < 1 or self.port >= 0xFFFF:
            raise ValueError('port is invalid')

