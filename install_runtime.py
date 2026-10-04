import os
import time

import httpx

PISTON_URL = os.environ["PISTON_URL"].rstrip("/")


def wait_for_piston() -> list[dict]:
    print("Waiting for the Piston API...")
    deadline = time.monotonic() + 120

    while True:
        try:
            response = httpx.get(f"{PISTON_URL}/api/v2/runtimes", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            if time.monotonic() >= deadline:
                raise SystemExit("Timed out waiting for the Piston API")
            time.sleep(1)


def has_c_and_cpp(runtimes: list[dict]) -> bool:
    languages = set()
    for runtime in runtimes:
        languages.add(runtime["language"])
        languages.update(runtime.get("aliases", []))
    return {"c", "c++"}.issubset(languages)


def install_gcc() -> None:
    print("Installing gcc (this may take a while)...")
    response = httpx.post(
        f"{PISTON_URL}/api/v2/packages",
        json={"language": "gcc", "version": "10.2.0"},
        timeout=1000,
    )
    response.raise_for_status()


def main() -> None:
    runtimes = wait_for_piston()

    if has_c_and_cpp(runtimes):
        print("gcc/c++ already installed.")
        return

    install_gcc()

    runtimes = httpx.get(f"{PISTON_URL}/api/v2/runtimes", timeout=10).json()
    if not has_c_and_cpp(runtimes):
        raise SystemExit("gcc installation did not register in /runtimes")

    print("gcc installed successfully.")


if __name__ == "__main__":
    main()
