import json
from pathlib import Path

import requests


PAYLOADS_FILE = Path("tests/payloads.json")

VULNERABLE_URL = "http://localhost:8000/chat"
PROTECTED_URL = "http://localhost:8001/chat"


def load_payloads() -> list[dict]:
    with PAYLOADS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def send_request(url: str, message: str) -> dict:
    try:
        response = requests.post(
            url,
            json={"message": message},
            timeout=120,
        )

        return {
            "status_code": response.status_code,
            "body": response.json(),
        }

    except requests.RequestException as error:
        return {
            "status_code": None,
            "body": {
                "error": str(error),
            },
        }


def main() -> None:
    payloads = load_payloads()
    results = []

    print(f"Загружено тестовых запросов: {len(payloads)}")
    print()

    for payload in payloads:
        test_id = payload["id"]
        category = payload["category"]
        message = payload["message"]

        print("=" * 70)
        print(f"Test ID: {test_id}")
        print(f"Category: {category}")
        print(f"Message: {message}")

        vulnerable_result = send_request(
            VULNERABLE_URL,
            message,
        )

        protected_result = send_request(
            PROTECTED_URL,
            message,
        )

        results.append(
            {
                "id": test_id,
                "category": category,
                "message": message,
                "vulnerable": vulnerable_result,
                "protected": protected_result,
            }
        )

        print()
        print("Vulnerable agent:")
        print(vulnerable_result)

        print()
        print("Protected agent:")
        print(protected_result)

        print()

        report_file = Path("tests/results.json")

        with report_file.open("w", encoding="utf-8") as file:
            json.dump(
                results,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(f"Отчёт сохранён: {report_file}")


if __name__ == "__main__":
    main()