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

### Configure Automation Hub

- Get token from https://console.redhat.com/ansible/automation-hub/token
- Set up the ansible.cfg with the token

### Install Collections

`ansible-galaxy collection install -r collections/requirements.yml`

### Configure AAP

`ansible-playbook setup_aap.yml -e aap_hostname=http://sandbox-aap -e aap_username=admin -e aap_password=${AAP_PASSWORD} -e aap_validate_certs=false`

### Set up the ServiceNow Credential

- Log into AAP, Automation Execution --> Credentials --> Service Now Demo Credential and update all fields

### Fire to Webhook

`python3 trigger_event.py --url https://xxx/eda-event-streams/api/eda/v1/external_event_stream/xxx`