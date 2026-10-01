#!/usr/bin/env python3

import json
import os
import sys

import requests

BASE_URL = os.getenv("SN_BASE_URL", "https://ven05174.service-now.com")
API_ENDPOINT = f"{BASE_URL}/api/now/table/incident"
USERNAME = os.getenv("SN_USERNAME", "your_servicenow_user")
PASSWORD = os.getenv("SN_PASSWORD", "your_servicenow_password")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def load_event():
    raw = os.getenv("EVENT_PAYLOAD_JSON", "")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def build_payload(event):
    event_type = event.get("event_type", "unknown")
    hostname = event.get("hostname", "unknown")
    detail = json.dumps(event, indent=2) if event else "No event payload provided"

    return {
        "short_description": os.getenv(
            "INCIDENT_SUMMARY", f"{event_type} alert on {hostname}"
        ),
        "description": os.getenv("INCIDENT_DETAIL", detail),
        "urgency": os.getenv("INCIDENT_URGENCY", "3"),
        "impact": os.getenv("INCIDENT_IMPACT", "3"),
        "category": "Hardware",
        "caller_id": "andrew.becker",
        "state": "1",
        "incident_state": "1",
    }


def create_incident():
    payload = build_payload(load_event())
    try:
        response = requests.post(
            API_ENDPOINT,
            auth=(USERNAME, PASSWORD),
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code == 201:
            result = response.json().get("result", {})
            print(
                json.dumps(
                    {
                        "success": True,
                        "number": result.get("number"),
                        "sys_id": result.get("sys_id"),
                        "state": result.get("incident_state"),
                        "instance": BASE_URL,
                        "short_description": payload.get("short_description"),
                    },
                    indent=2,
                )
            )
            sys.exit(0)

        print(
            json.dumps(
                {
                    "success": False,
                    "status_code": response.status_code,
                    "response": response.text,
                },
                indent=2,
            )
        )
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    create_incident()
