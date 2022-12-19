import asyncio
from typing import Self, Optional
from .client_params import ClientParams


class ClosedSessionException(Exception):
    pass


class Session:
    def __init__(self, params: ClientParams):
        self.params = params
        self.closed = True

    async def __aenter__(self) -> Self:
        self.reader, self.writer = await asyncio.open_connection(
            self.params.host, self.params.port)
        self.closed = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.closed = True
        self.writer.close()
        await self.writer.wait_closed()

    async def send_cmd(self, msg: str) -> Optional[str]:
        if self.closed:
            raise ClosedSessionException
        cmd = msg.encode()
        self.writer.write(cmd)
        self.writer.write(b'\n')
        await self.writer.drain()
        response = await self.reader.readline()
        if not response or not response.endswith(b'\n'):
            return None
        return response[:-1].decode()
