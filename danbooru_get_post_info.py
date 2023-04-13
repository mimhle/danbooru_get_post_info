"""Get post info from danbooru.donmai.us

Usage:
    python danbooru_get_post_info.py <start> [<stop>] [-t <timeout>] [-r <retry>]
    python danbooru_get_post_info.py <id> [-t <timeout>] [-r <retry>]
    python danbooru_get_post_info.py -h | --help

Options:
    -h --help       Show this screen.
    -t --timeout    Timeout in seconds (for all posts) [default: 3600].
    -r --retry      Retry times [default: 10].

Returns:
    A json file with post info.
"""

import argparse
import time
import json
import requests
from tqdm.auto import tqdm


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"'{func.__name__}' took {end_time - start_time:.6f}s")
        return result

    return wrapper


@timer
def danbooru_post_info_request(min_id=1, max_id=10000000, timeout=43200, max_attempts=10):
    result = []
    time_ = time.time() + timeout
    response_json = {}
    with tqdm(total=max_id - min_id + 1) as pb:
        for i in range(min_id, max_id + 1):
            for attempt in range(max_attempts):
                try:
                    if not i % 10 - 1:
                        if (curr_time := time.time()) >= time_:
                            return result + [f"Stop at {i}, timeout {round(curr_time - (time_ - timeout), 1)}s in"]
                    response = requests.get(f"https://danbooru.donmai.us/posts/{i}.json")
                    response_json = response.json()
                except KeyboardInterrupt:
                    return result + [f"Stop at {i}, keyboard interrupt"]
                except Exception as error:
                    if attempt >= max_attempts - 1:
                        return result + [f"Stop at {i}, error {error}, response {response}"]
                    else:
                        time.sleep(0.1)
                        continue
                else:
                    break
            result.append(response_json)
            pb.update(1)
    return result


@timer
def save_to_json(inputs, file_name_and_path):
    with open(file_name_and_path, mode='w') as file:
        json.dump(inputs, file, indent=2)


def main(start, stop=None, timeout=3600, max_attempts=10):
    if not stop:
        stop = start
    post_info = danbooru_post_info_request(start, stop, timeout, max_attempts)
    if isinstance(post_info[-1], str):
        print(post_info[-1])
    file_name = f"{start}-{stop}.json" if start != stop else f"{start}.json"
    save_to_json(post_info, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int, help="start id")
    parser.add_argument("stop", type=int, nargs="?", help="stop id")
    parser.add_argument("-t", "--timeout", type=int, default=3600, help="timeout in seconds (all posts) (default: 3600)")
    parser.add_argument("-r", "--retry", type=int, default=10, help="max retry attempts (default: 10)")
    args = parser.parse_args()
    main(args.start, args.stop, args.timeout, args.retry)
