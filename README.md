# ansible-webhooks-to-python-scripts

Demo that shows EDA event streams → rulebook activations → a Controller job template that creates a ServiceNow incident via a Python script.

It supports two demo angles:

1. **Platform isolation** — separate event streams, activations, and rulebooks for disk vs CPU
2. **Rulebook complexity** — one rulebook that handles both event types

## Architecture

| Event stream | Activation | Rulebook |
| --- | --- | --- |
| Disk Usage Event Stream | `disk_usage_webhook` | `disk_usage_alerts.yml` (disk only → script JT) |
| Disk Usage Event Stream | `disk_usage_webhook_itsm` | `disk_usage_alerts_itsm.yml` (disk only → ITSM JT) |
| CPU Usage Event Stream | `cpu_usage_webhook` | `cpu_usage_alerts.yml` (CPU only) |
| Combined Usage Event Stream | `combined_usage_webhook` | `combined_usage_alerts.yml` (disk + CPU) |

A disk event posted to the Disk Usage Event Stream is delivered to both disk activations, so you get a side-by-side script vs `servicenow.itsm` contrast from one POST.

### Script vs Ansible-native ServiceNow

Two job templates share the same `event_payload` contract:

| Job template | Playbook | Integration |
| --- | --- | --- |
| `open_snow_incident` | `playbooks/run_snow_incident_script.yml` | Python script (`requests`) |
| `open_snow_incident_itsm` | `playbooks/run_snow_incident_itsm.yml` | `servicenow.itsm.incident` |

The disk ITSM rulebook/activation is wired to the shared disk stream. CPU and combined paths still use the script JT by default.

## Demo setup

This demo assumes you have a Red Hat account.

### Provision resources (sandbox.redhat.com)

- Open this repo in Dev Spaces
- Launch an AAP instance
- After AAP provisions, log in with the provided credentials and attach an AAP trial from the subscription page

### Configure Automation Hub

- Get a token from https://console.redhat.com/ansible/automation-hub/token
- Set the token in `ansible.cfg`

### Install collections

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

### Configure AAP

```bash
cp config_as_code/aap_secrets.yml.example config_as_code/aap_secrets.yml
# Populate with reasonable values
ansible-playbook config_as_code/setup_aap.yml
```

### Set up the ServiceNow credential

In AAP: **Automation Execution → Credentials → ServiceNow Demo** and update all fields.

### Sync projects after pulling rulebook changes

Ensure the Controller and EDA projects for this repo have pulled the latest content (or re-run `setup_aap.yml`), then confirm the three activations are running.

## Fire events

Use `scripts/trigger_event.py` to POST a hardcoded payload to an event stream URL. Choose the stream URL for the demo path you want, and `--type` for the payload.

Auth defaults match config-as-code (`redhat` / `redhat`).

```bash
# Disk-only path (platform isolation)
python3 scripts/trigger_event.py \
  --url <DISK_USAGE_EVENT_STREAM_URL> \
  --type disk \
  --username redhat \
  --password redhat \
  --insecure

# CPU-only path (platform isolation)
python3 scripts/trigger_event.py \
  --url <CPU_USAGE_EVENT_STREAM_URL> \
  --type cpu \
  --username redhat \
  --password redhat \
  --insecure

# Combined path — disk event (rulebook complexity)
python3 scripts/trigger_event.py \
  --url <COMBINED_USAGE_EVENT_STREAM_URL> \
  --type disk \
  --username redhat \
  --password redhat \
  --insecure

# Combined path — CPU event (rulebook complexity)
python3 scripts/trigger_event.py \
  --url <COMBINED_USAGE_EVENT_STREAM_URL> \
  --type cpu \
  --username redhat \
  --password redhat \
  --insecure
```

Event stream URLs are shown in AAP under **Automation Decisions → Event Streams**.

### Expected results

- Disk event to the disk stream → SNOW incident with disk details (hostname, disk, disk_percent)
- CPU event to the CPU stream → SNOW incident with CPU details (hostname, cpu_percent)
- Disk or CPU event to the combined stream → handled by the combined rulebook → SNOW incident populated from that event

Cross-posting the wrong type to a single-type stream (for example `--type cpu` to the disk stream) should not match that rulebook's conditions.
