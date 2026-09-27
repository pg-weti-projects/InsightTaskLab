import requests
from django.conf import settings


class Judge0Error(Exception):
    pass


class Judge0Client:
    def __init__(self):
        self.base_url = getattr(
            settings,
            "JUDGE0_URL",
            "http://judge0-server:2358",
        ).rstrip("/")

        self.session = requests.Session()

    def submit(
        self,
        *,
        source_code,
        stdin="",
        language_id=54,
    ):
        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin,
            "cpu_time_limit": 2.0,
            "wall_time_limit": 10.0,
            "memory_limit": 128000,
            "enable_per_process_and_thread_time_limit": True,
            "enable_per_process_and_thread_memory_limit": True,
        }

        response = self.session.post(
            f"{self.base_url}/submissions",
            params={"base64_encoded": "false"},
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        token = data.get("token")

        if not token:
            raise Judge0Error(f"Judge0 nie zwrócił tokenu: {data}")

        return data

    def get_submission(self, token):
        response = self.session.get(
            f"{self.base_url}/submissions/{token}",
            params={"base64_encoded": "false"},
            timeout=10,
        )

        response.raise_for_status()

        return response.json()
