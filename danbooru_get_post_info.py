"""Get post info from danbooru.donmai.us

Usage:
    python danbooru_get_post_info.py <start> [<stop>] [-t <timeout>] [-r <retry>]
    python danbooru_get_post_info.py <id> [-t <timeout>] [-r <retry>]
    python danbooru_get_post_info.py -h | --help

Options:
    <start>       Start id.
    [<stop>]        Stop id [default: <start>].
    -h --help       Show this screen.
    -f --file       File name and path to save the result [default: <start>-<stop>.json].
    -t --timeout    Timeout in seconds for each request [default: 300].
    -r --retry      Max retries [default: 100].
    --cooldown   Cooldown in seconds finishing each request [default: 1].
    --concurrency   Max concurrent requests [default: 5].


Returns:
    A json file with post info.
"""

import os
from typing import Iterable
import asyncio
import time
import argparse
import json
import aiohttp
from tqdm.asyncio import tqdm as atqdm


def timer(func: callable) -> callable:
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"'{func.__name__}' took {end_time - start_time:.6f}s")
        return result

    return wrapper


@timer
def save_to_json(inputs: list[dict], file_name_and_path: str) -> None:
    with open(file_name_and_path, mode='w') as file:
        json.dump(inputs, file, indent=2)


@timer
def get_post_info(
        start: int = 1,
        end: int = 100,
        *,
        batch_size: int = None,
        concurrency: int = 10,
        timeout: int = 60 * 60 * 2,
        max_attempts: int = 1000,
        cooldown: int = 1,
) -> list[dict]:
    # split list to chunks
    def split_chunk(inp: Iterable, chunk_size: int) -> Iterable[tuple]:
        chunks = []
        while inp:
            chunks.append(tuple(inp[:chunk_size]))
            inp = inp[chunk_size:]
        return chunks

    # convert list of ids to urls
    def get_urls(ids: Iterable[int]) -> Iterable[str]:
        return (f"https://danbooru.donmai.us/posts/{i}.json" for i in ids)

    # get the response for 1 url
    async def get_request(url: str, *, session: aiohttp.ClientSession, retries: int = max_attempts) -> dict:
        async with session.get(url) as response:
            content_type = response.headers.get("Content-Type")

            for _ in range(retries):
                if "application/json" not in content_type:
                    await asyncio.sleep(cooldown)
                    continue
                else:
                    try:
                        data = await response.read()
                        await asyncio.sleep(cooldown)
                        return json.loads(data)
                    except Exception as e:
                        print(f"{url}: {e}")
                        await asyncio.sleep(cooldown)
                        continue
            else:
                return {"Error": [f"{url}: Max retries reached"]}

    # get the response for multiple urls
    async def get_requests(urls: Iterable[str]) -> list[dict]:
        connector = aiohttp.TCPConnector(limit=concurrency)
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        semaphore = asyncio.Semaphore(concurrency)

        async with semaphore:
            async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as session:
                tasks = [asyncio.create_task(get_request(url, session=session)) for url in urls]
                results = await atqdm.gather(*tasks)
                return results

    # generate urls
    ids = range(start, end + 1)
    urls = tuple(get_urls(ids))
    if batch_size:
        urls = split_chunk(urls, batch_size)
    else:
        urls = [urls]

    # get responses
    print(f"Total batch count: {len(urls)}")
    result = []
    for i, batch in enumerate(urls):
        print(f"Current batch: {i + 1}")
        result.extend(asyncio.run(get_requests(batch)))
    return result


def main(start: int, stop: int, file_path: str = None, **kwargs) -> None:
    if not stop:
        stop = start

    if file_path:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_name = file_path
    else:
        file_name = f"{start}-{stop}.json" if start != stop else f"{start}.json"

    save_to_json(get_post_info(start, stop, **kwargs), file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int, help="Start id")
    parser.add_argument("stop", type=int, nargs="?", help="Stop id")
    parser.add_argument("-f", "--file", type=str, nargs="?", help="File path (save to current directory with format: <start>-<stop>.json if not specified)")
    parser.add_argument("-t", "--timeout", type=int, default=300, help="Timeout in seconds for each request (default: 300)")
    parser.add_argument("-r", "--retry", type=int, default=100, help="Max retry attempts (default: 100)")
    parser.add_argument("-b", "--batch-size", type=int, default=100, help="Batch size (default: 100)")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests (default: 5)")
    parser.add_argument("--cooldown", type=int, default=1, help="Cooldown in seconds finishing each request (default: 1)")
    args = parser.parse_args()
    main(
        args.start,
        args.stop,
        file_path=args.file,
        timeout=args.timeout,
        max_attempts=args.retry,
        batch_size=args.batch_size,
        concurrency=args.concurrency,
        cooldown=args.cooldown,
    )
