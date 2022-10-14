import asyncio
import time
from collections import deque

import pandas as pd


async def async_ping(host, semaphore):
    async with semaphore:
        for _ in range(5):
            proc = await asyncio.create_subprocess_shell(
                f'C:\\Windows\\System32\\ping {host} -n 1 -w 1 -l 1',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            status = await proc.wait()
            if status == 0:
                return 'Alive'

        return 'Timeout'


async def async_main(hosts, limit):
    semaphore = asyncio.Semaphore(limit)
    tasks1 = deque()
    for host in hosts:
        tasks1.append(asyncio.create_task(
            async_ping(host, semaphore))
        )
    return (t1 for t1 in await asyncio.gather(*tasks1))


host_df = pd.read_csv('output_for_ping.csv')

# set concurrent task limit
limit = 256

start = time.perf_counter()

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
resp = loop.run_until_complete(async_main(host_df['IP'].to_list(), limit))
loop.close()

finish = time.perf_counter()

host_df['Status'] = list(resp)
print(host_df)
host_df.to_csv('ouput_test_ping.csv')
print(f'Runtime: {round(finish-start,4)} seconds')