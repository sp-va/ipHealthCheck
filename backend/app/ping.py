import asyncio
import typing as t
import subprocess as sp
import re
from concurrent.futures import ThreadPoolExecutor

from app.schemas import PingOutput


def ping_ip(address: str):
    try:
        output = (sp.check_output(["ping", "-n", "-c", "1", "-W", "1", address])).decode()
        packet_loss_percentage = re.search(
            r"(\d+)% packet loss",
            output
        )

        packet_loss_percentage = int(packet_loss_percentage.group(1))
        rtt_avg = re.search(
            r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms",
            output
        )
        rtt_avg = float(rtt_avg.group(1))
        return PingOutput(
            address=address,
            packet_loss=packet_loss_percentage,
            avg_ping_ms=rtt_avg
        )
    except sp.CalledProcessError:
        return PingOutput(
            address=address,
            packet_loss=None,
            avg_ping_ms=None
        )


async def run_multithread_pings(addresses: t.Set[str]):
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=5) as excr:
        tasks = [loop.run_in_executor(excr, ping_ip, address) for address in addresses]
        return await asyncio.gather(*tasks)