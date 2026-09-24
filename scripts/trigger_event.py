#!/usr/bin/env python3

import argparse
import json
import os
import sys

import requests


EXAMPLE_COMMAND = """
python scripts/trigger_event.py \
  --url https://aap.example.com/eda/event-streams/.../ \
  --username redhat \
  --password redhat \
  --insecure
"""

DEFAULT_PAYLOAD = {
    "hostname": "andrew-ansible-demo.example.com",
    "disks": [
        {
            "name": "disk1",
            "use_percent": "45%",
        }
    ],
}


def trigger_event(url, payload, username=None, password=None, verify=True):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    auth = (username, password) if username and password else None

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        auth=auth,
        verify=verify,
        timeout=30,
    )

    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)

    response.raise_for_status()
    return response


def main():
    parser = argparse.ArgumentParser(
        description="POST a disk-usage event to an AAP EDA event stream"
    )
    parser.add_argument(
        "--url",
        default=os.getenv("EVENT_STREAM_URL"),
        help="Event stream URL (or set EVENT_STREAM_URL)",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("EVENT_STREAM_USERNAME"),
        help="Basic Event Stream username (or set EVENT_STREAM_USERNAME)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("EVENT_STREAM_PASSWORD"),
        help="Basic Event Stream password (or set EVENT_STREAM_PASSWORD)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification",
    )
    args = parser.parse_args()

    if not args.url:
        parser.error("event stream URL is required via --url or EVENT_STREAM_URL")

    try:
        trigger_event(
            url=args.url,
            payload=DEFAULT_PAYLOAD,
            username=args.username,
            password=args.password,
            verify=not args.insecure,
        )
    except requests.exceptions.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
