#Turn on tv (taskScheduler)
import json
import asyncio
from wakeonlan import send_magic_packet
from websockets import connect
with open("config.json") as f:
    config: dict = json.load(f)


async def ping_tv_simple() -> bool:
    send_magic_packet(config['mac_address_tv'], ip_address=config['broadcast'])
    for _ in range(10):
        try:
            async with connect(f"ws://{config['ip_tv']}:3000", open_timeout=4) as tv:
                return tv.open
        except asyncio.exceptions.TimeoutError:
            continue

asyncio.run(ping_tv_simple())

