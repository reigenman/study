import asyncio
import logging
import aioconsole
import sys
from typing import Iterator, Optional
from led_proto.client import *
from simple_parsing import ArgumentParser



FORMAT = '%(levelname)s %(asctime)s %(message)s'
logger = logging.getLogger(__name__)


def _parse_args() -> ClientParams:
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, default='127.0.0.1', help='host')
    parser.add_argument("--port", type=int, default=9999, help='port')
    args = parser.parse_args()
    try:
        return ClientParams(args.host, args.port)
    except ValueError as e:
        print(f'invalid params: {str(e)}')
        sys.exit(2)


def _delay_seconds(first: float = 1.0, max_delay: float = 4.0, exp: float = 2.0) -> Iterator[float]:
    value = first
    while True:
        yield value
        value = min(max_delay, value * exp)


async def run_client(client_params: ClientParams) -> None:
    try:
        delay = _delay_seconds()
        while True:
            if await run_session(client_params):
                delay = _delay_seconds()
            sleep_seconds = next(delay)
            await asyncio.sleep(sleep_seconds)
    except (EOFError, asyncio.CancelledError):
        logger.info('Session was finished by user')


async def run_session(client_params: ClientParams) -> bool:
    logger.info(f'Connecting to {client_params}')
    at_least_one_cmd_success = False
    try:
        async with Session(client_params) as session:
            while True:
                cmd = await aioconsole.ainput('Enter cmd:\n')
                response = await session.send_cmd(cmd)
                if not response:
                    logger.error("Session is closed by remote")
                    break
                at_least_one_cmd_success = True
                await aioconsole.aprint(f'Response: {response}')
    except OSError as e:
        logger.error(f'session failed with error: {e}')
    return at_least_one_cmd_success


def main():
    client_params = _parse_args()
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    asyncio.run(run_client(client_params))


if __name__ == '__main__':
    main()
