import argparse
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

REQUEST_COUNT = 10
TIMEOUT = 60
CHUNK_SIZE = 8192

def validate(url: str) -> str:
    try:
        parsed = urlsplit(url)
    except ValueError:
        raise argparse.ArgumentTypeError("Некорректный URL")

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise argparse.ArgumentTypeError("Use valid URL that starts with 'http://' or 'https://'")

    return url

def download(url):
    request = Request(url)
    total_bytes = 0

    start_time = time.perf_counter()

    with urlopen(request, timeout=60) as response:
        while chunk := response.read(8192):
            total_bytes += len(chunk)

    elapsed_time = time.perf_counter() - start_time

    return elapsed_time, total_bytes

def format_error(e):
    if isinstance(e, HTTPError):
        return f"HTTP error {e.code}: {e.reason}"

    if isinstance(e, URLError):
        return f"Network error: {e.reason}"

    if isinstance(e, TimeoutError):
        return f"Request timed out after {TIMEOUT} seconds"

    return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Measure your download speed via HTTP/HTTPS"
    )

    parser.add_argument(
        "url",
        type=validate,
        help="URL to download (example: 'https://images.unsplash.com/photo-1793640439641-1d9d454c3a7a'",
    )

    args = parser.parse_args()

    total_time = 0
    total_bytes = 0
    successful_requests = 0

    print(f"Starting speed test: {args.url}")
    print(f"Number of requests: {REQUEST_COUNT}\n")

    try:
        for i in range(REQUEST_COUNT):
            elapsed_time, downloaded_bytes = download(args.url)

            total_time += elapsed_time
            total_bytes += downloaded_bytes
            successful_requests += 1

            print(
                f"Request {i + 1}/{REQUEST_COUNT}: "
                f"{left:.2f} sec |"
                f"{done / 1_000_000:.2f} MB"
            )
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        print(f"\n{format_error(e)}")
        print(f"Number of successful requests: {successful_requests} / {REQUEST_COUNT}\n")
        return

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return

    avg_time = total_time / successful_requests
    avg_speed = total_bytes / total_time / 1_000_000

    print("Speed test results:\n")
    print(f"Avg request time: {avg_time:.2f} sec")
    print(f"Data downloaded: {total_bytes / 1_000_000:.2f} MB")
    print(f"Avg download speed: {avg_speed:.2f} MB/s")

if __name__ == "__main__":
    main()