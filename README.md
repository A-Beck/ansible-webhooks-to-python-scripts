# ansible-webhooks-to-python-scripts

This repo sets up a basic demo:

- EDA recieves an event via webhook
- It launches a job
- That job creates a record in service now

## Demo Setup

This demo assumes you have a Red hat Accounot

### Provision resources sandbox.redhat.com account

- Open this repo in dev spaces
- Launch an AAP instance
- After AAP Instance Provisions, log in with the provided credentials. You should be able to attach an AAP trial from the subscription page.

### Open Dev Spaces, Configure your environment, and run the demo

### Configure Automation Hub

- Get token from https://console.redhat.com/ansible/automation-hub/token
- Set up the `ansible.cfg` with the token

### Install Collections

- `ansible-galaxy collection install -r collections/requirements.yml`

### Configure AAP

- Copy `aap_secrets.yml.example` to `aap_secrets.yml`
- Populate with reasonable values
- Run `ansible-playbook setup_aap.yml`

### Set up the ServiceNow Credential

- Log into AAP, Automation Execution --> Credentials --> Service Now Demo Credential and update all fields

### Fire to Webhook

`python3 trigger_event.py --url https://xxx/eda-event-streams/api/eda/v1/external_event_stream/xxx`