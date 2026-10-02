import json
import os
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

PISTON_URL = os.environ["PISTON_URL"].rstrip("/")


def api(path, payload=None, timeout=5):
    body = None if payload is None else json.dumps(payload).encode()
    request = Request(
        f"{PISTON_URL}/api/v2/{path}",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def has_c_and_cpp(runtimes):
    languages = set()
    for runtime in runtimes:
        languages.add(runtime["language"])
        languages.update(runtime.get("aliases", []))
    return {"c", "c++"}.issubset(languages)


print("Loading API Pistona...")
deadline = time.monotonic() + 120

while True:
    try:
        runtimes = api("runtimes", timeout=10)
        break
    except (URLError, TimeoutError, ConnectionError):
        if time.monotonic() >= deadline:
            raise SystemExit("Timed out for API Pistona loading")
        time.sleep(1)
if has_c_and_cpp(runtimes):
    print("Pistona is already installed")
else:
    print("The first installation of GCC. It may take a while...")
    api("packages", {"language": "gcc", "version": "10.2.0"}, timeout=12000)

    runtimes = api("runtimes")

    if not has_c_and_cpp(runtimes):
        raise SystemExit("The first installation of GCC failed")

    print("Pistona is now installed")
