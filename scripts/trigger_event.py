#!/usr/bin/env python3

import requests
import json

def trigger_event(event_type, payload):
    url = "http://localhost:5000/events"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "event_type": event_type,
        "payload": payload
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json()

if __name__ == "__main__":
    payload = {
        "hostname": "andrew-ansible-demo.example.com",
        "disks": [
            {
                "name": "disk1",
                "use_percent": "45%"
            }
        ]
    }