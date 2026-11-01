import argparse
import asyncio
import random
import statistics
import time
import uuid
from collections import Counter
from dataclasses import dataclass

import httpx


SNIPPETS = {
    "hello": (
        '#include <iostream>\nint main(){ std::cout << "Hello"; }\n',
        "Hello",
    ),
    "medium": (
        (
            "#include <iostream>\n"
            "#include <numeric>\n"
            "#include <vector>\n"
            "int main(){ std::vector<int> v(100000); std::iota(v.begin(), v.end(), 0);\n"
            "  long long s = 0; for (int x : v) s += x; std::cout << s; }\n"
        ),
        "4999950000",
    ),
    "heavy": (
        (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n"
            "int main(){ vector<int> v(100000); iota(v.begin(), v.end(), 0);\n"
            "  long long s = 0; for (int x : v) s += x; cout << s; }\n"
        ),
        "4999950000",
    ),
}


def make_unique(code: str) -> str:
    """Append a random comment so the backend cache can't serve the result."""
    return f"{code}// {uuid.uuid4().hex}\n"


@dataclass
class Result:
    latency: float
    ok: bool
    error: str | None = None


def check_response(response: httpx.Response, expect: str) -> str | None:
    """Return None if the response is correct, otherwise a short error text."""
    if response.status_code != 200:
        return f"HTTP {response.status_code}"
    body = response.json()
    if body.get("exit_code") != 0:
        details = body.get("stderr") or body.get("compile_stderr")
        return f"exit_code={body.get('exit_code')}: {details}"[:120]
    if expect not in (body.get("stdout") or ""):
        return "unexpected stdout"
    return None


async def one_request(client, url, code, delay, expect) -> Result:
    await asyncio.sleep(delay)
    start = time.perf_counter()
    try:
        response = await client.post(url, json={"source_code": code})
        error = check_response(response, expect)
    except httpx.TimeoutException:
        error = "client timeout"
    except httpx.HTTPError as e:
        error = f"{type(e).__name__}: {e}"[:120]
    return Result(time.perf_counter() - start, error is None, error)


def percentile(sorted_values, p):
    index = round(p / 100 * (len(sorted_values) - 1))
    return sorted_values[index]


def make_delays(args):
    if args.mode == "burst":
        return [0.0] * args.n
    return [random.uniform(0, args.spread) for _ in range(args.n)]


def print_report(results, wall, args, round_no):
    latencies = sorted(r.latency for r in results)
    successes = sum(r.ok for r in results)

    print(
        f"\n--- round {round_no} | {args.mode} | {args.n} users | code={args.code} ---"
    )
    print(f"success: {successes}/{len(results)}   wall time: {wall:.1f}s")
    print(
        f"latency  min {latencies[0]:.2f}s  p50 {percentile(latencies, 50):.2f}s  "
        f"p95 {percentile(latencies, 95):.2f}s  max {latencies[-1]:.2f}s  "
        f"mean {statistics.mean(latencies):.2f}s"
    )
    for error, count in Counter(r.error for r in results if not r.ok).most_common():
        print(f"  {count:>3} x {error}")


async def run_round(args, code, expect, round_no) -> int:
    limits = httpx.Limits(max_connections=args.n + 10)
    async with httpx.AsyncClient(timeout=args.timeout, limits=limits) as client:
        tasks = [
            one_request(
                client,
                args.url,
                code if args.same_code else make_unique(code),
                d,
                expect,
            )
            for d in make_delays(args)
        ]
        start = time.perf_counter()
        results = await asyncio.gather(*tasks)
        wall = time.perf_counter() - start

    print_report(results, wall, args, round_no)
    return sum(r.ok for r in results)


async def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--url", default="http://localhost:8000/api/code-execution/run/")
    ap.add_argument("-n", type=int, default=30, help="simultaneous users (default 30)")
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--mode", choices=["burst", "spread"], default="burst")
    ap.add_argument(
        "--spread", type=float, default=10.0, help="seconds, for --mode spread"
    )
    ap.add_argument("--code", choices=list(SNIPPETS), default="heavy")
    ap.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="client timeout per request, seconds",
    )
    ap.add_argument("--pause", type=float, default=2.0, help="seconds between rounds")
    ap.add_argument(
        "--same-code",
        action="store_true",
        help="send identical code every time (measures the cache instead of Piston)",
    )
    args = ap.parse_args()

    code, expect = SNIPPETS[args.code]

    # Warm-up: one request, so first-time effects don't skew the burst.
    async with httpx.AsyncClient(timeout=args.timeout) as c:
        try:
            r = await c.post(args.url, json={"source_code": make_unique(code)})
            print(f"warm-up: HTTP {r.status_code}")
        except httpx.HTTPError as e:
            raise SystemExit(f"Cannot reach {args.url}: {e}")

    count = 0
    for i in range(args.rounds):
        count += await run_round(args, code, expect, i)
        if i < args.rounds - 1:
            await asyncio.sleep(args.pause)
    print(f"\nTOTAL success: {count}/{args.n * args.rounds}")


if __name__ == "__main__":
    asyncio.run(main())
