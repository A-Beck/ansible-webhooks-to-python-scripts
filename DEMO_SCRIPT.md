# Demo script

Ordered steps to set up and run the EDA → Controller → ServiceNow demo.

## What you will show

1. **Platform isolation** — separate streams / activations / rulebooks for disk vs CPU
2. **Rulebook complexity** — one combined rulebook handling both event types
3. **Script vs Ansible-native** — one disk POST fires both the Python script JT and `servicenow.itsm`

---

## 0. Prerequisites

- Red Hat account
- This repo open in Dev Spaces (or a similar workspace with `ansible-playbook` / collections)
- An AAP instance provisioned from [sandbox.redhat.com](https://sandbox.redhat.com)
- A ServiceNow instance you can create incidents in
- Automation Hub token: https://console.redhat.com/ansible/automation-hub/token

After AAP is up, log in and attach an AAP trial subscription if prompted.

---

## 1. Configure the workspace

### 1.1 Automation Hub (local galaxy CLI)

Put your Hub token in `ansible.cfg` (see `ansible.cfg.local` for the server list pattern).

### 1.2 Install collections

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

### 1.3 Secrets for config-as-code

```bash
cp config_as_code/aap_secrets.yml.example config_as_code/aap_secrets.yml
```

Edit `config_as_code/aap_secrets.yml`:

| Field | Value |
| --- | --- |
| `aap_hostname` | Your AAP URL |
| `aap_username` | AAP admin user |
| `aap_password` | Prefer env `AAP_PASSWORD` (Dev Spaces injects this) |
| `ah_token` | Automation Hub offline token |
| `sn_base_url` / `sn_username` / `sn_password` | ServiceNow instance |

Confirm `AAP_PASSWORD` is set in the shell (`echo $AAP_PASSWORD`).

---

## 2. Apply AAP configuration

```bash
ansible-playbook config_as_code/setup_aap.yml
```

This creates (among other objects):

- ServiceNow + Automation Hub credentials (Hub creds attached to **Default**)
- Controller project, inventory, JTs `open_snow_incident` and `open_snow_incident_itsm`
- 3 event streams, 4 rulebook activations, decision environment

### 2.1 Finish ServiceNow credential (if placeholders remain)

**Automation Execution → Credentials → ServiceNow Demo** — set real base URL / user / password.

### 2.2 Confirm activations are running

**Automation Decisions → Rulebook Activations** — all four should be **Running**:

- `disk_usage_webhook`
- `disk_usage_webhook_itsm`
- `cpu_usage_webhook`
- `combined_usage_webhook`

If rulebooks are missing after a git change, sync the EDA/Controller projects (or re-run `setup_aap.yml`).

---

## 3. Load event stream URLs

```bash
ansible-playbook config_as_code/export_event_stream_urls.yml
source config_as_code/event_stream_urls.env
```

You should have:

- `DISK_USAGE_EVENT_STREAM_URL`
- `CPU_USAGE_EVENT_STREAM_URL`
- `COMBINED_USAGE_EVENT_STREAM_URL`

Stream basic auth defaults in `trigger_event.py`: user `redhat` / password `redhat` (TLS verify off).

---

## 4. Exercise the demo

Use the same helper for every POST:

```bash
python3 scripts/trigger_event.py \
  --url "$SOME_STREAM_URL" \
  --type disk|cpu
```

Watch **Automation Execution → Jobs** and ServiceNow for incidents. Event fields (`event_type`, `hostname`, metrics) should appear in the incident summary/description.

### Facet A — Platform isolation (disk)

```bash
python3 scripts/trigger_event.py \
  --url "$DISK_USAGE_EVENT_STREAM_URL" \
  --type disk
```

**Expect:** Two jobs / two incidents from one POST:

| Activation | Job template | Integration |
| --- | --- | --- |
| `disk_usage_webhook` | `open_snow_incident` | Python script |
| `disk_usage_webhook_itsm` | `open_snow_incident_itsm` | `servicenow.itsm.incident` |

Talking point: same event stream, two activations — thin script launcher vs certified collection.

### Facet B — Platform isolation (CPU)

```bash
python3 scripts/trigger_event.py \
  --url "$CPU_USAGE_EVENT_STREAM_URL" \
  --type cpu
```

**Expect:** One job via `cpu_usage_webhook` → `open_snow_incident` (script path), CPU details in SNOW.

Optional contrast: `--type disk` to the CPU stream should **not** fire the CPU-only rulebook.

### Facet C — Rulebook complexity (combined stream)

```bash
# Disk event on the combined stream
python3 scripts/trigger_event.py \
  --url "$COMBINED_USAGE_EVENT_STREAM_URL" \
  --type disk

# CPU event on the combined stream
python3 scripts/trigger_event.py \
  --url "$COMBINED_USAGE_EVENT_STREAM_URL" \
  --type cpu
```

**Expect:** Both handled by `combined_usage_webhook` / `combined_usage_alerts.yml` (two rules in one rulebook).

Talking point: isolation at the platform layer (separate streams) vs logic density in a single rulebook.

---

## 5. Suggested live narrative (short)

1. Sketch the table: stream → activation → rulebook → JT → SNOW  
2. Run **Facet A** — one disk POST, two differently implemented incidents  
3. Run **Facet B** — dedicated CPU path  
4. Run **Facet C** — same rulebook, two event types  
5. Optionally open the thin playbook (`run_snow_incident_script.yml`) vs the ITSM playbook to compare overhead

---

## Quick command cheat sheet

```bash
# Setup (once)
ansible-galaxy collection install -r collections/requirements.yml
cp config_as_code/aap_secrets.yml.example config_as_code/aap_secrets.yml
# edit aap_secrets.yml
ansible-playbook config_as_code/setup_aap.yml
ansible-playbook config_as_code/export_event_stream_urls.yml
source config_as_code/event_stream_urls.env

# Demo POSTs
python3 scripts/trigger_event.py --url "$DISK_USAGE_EVENT_STREAM_URL" --type disk
python3 scripts/trigger_event.py --url "$CPU_USAGE_EVENT_STREAM_URL" --type cpu
python3 scripts/trigger_event.py --url "$COMBINED_USAGE_EVENT_STREAM_URL" --type disk
python3 scripts/trigger_event.py --url "$COMBINED_USAGE_EVENT_STREAM_URL" --type cpu
```
