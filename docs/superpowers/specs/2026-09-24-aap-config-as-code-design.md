# AAP Config-as-Code Design — Controller Job Path

**Date:** 2026-09-24  
**Status:** Approved for implementation planning  
**Collection:** [infra.aap_configuration](https://galaxy.ansible.com/ui/repo/published/infra/aap_configuration/content/)

## Goal

Define a standard Ansible Automation Platform (AAP) config-as-code variable structure and apply playbook so a demo Controller can create:

1. A custom ServiceNow credential type and credential
2. A Git project pointing at this repository
3. A localhost inventory
4. A job template that runs `playbooks/run_snow_incident_script.yml`

This is the Controller half of the webhook → rulebook → job template → Python script demo. EDA objects are out of scope for this pass.

## Approach

**Single vars file + dispatch role**

- `config_as_code/aap_vars.yml` holds all Controller object lists using `infra.aap_configuration` standard variable names
- `config_as_code/setup_aap.yml` loads those vars and runs `infra.aap_configuration.dispatch`
- `collections/requirements.yml` pins required collections

Rejected alternatives: split `configs/*.yml` (more files than needed for a small demo); vars-only stub (not applyable).

## File layout

```text
collections/requirements.yml
config_as_code/
  aap_vars.yml      # controller_* object lists
  setup_aap.yml     # include_vars + dispatch
```

AAP API auth (`aap_hostname`, `aap_username`/`aap_password` or `aap_token`, `aap_validate_certs`) is **not** committed. Pass via extra vars or a local untracked file when applying.

## Organization

All objects live in the existing **`Default`** organization. No `aap_organizations` entry is required.

## Object definitions

### Credential type — `ServiceNow`

Variable: `controller_credential_types`

| Field | Value |
|-------|--------|
| name | `ServiceNow` |
| kind | `cloud` |
| inputs.fields | `sn_base_url` (string), `sn_username` (string), `sn_password` (string, secret) |
| inputs.required | all three fields |
| injectors.env | `SN_BASE_URL`, `SN_USERNAME`, `SN_PASSWORD` |

Injector values use `!unsafe "{{ field_id }}"` so Ansible does not template them before Controller receives the literal Jinja. Env names match `scripts/create_snow_incident.py` (`os.getenv("SN_*")`).

### Credential — `ServiceNow Demo`

Variable: `controller_credentials`

| Field | Value |
|-------|--------|
| name | `ServiceNow Demo` |
| organization | `Default` |
| credential_type | `ServiceNow` |
| inputs.sn_base_url | `CHANGE_ME` (placeholder) |
| inputs.sn_username | `CHANGE_ME` |
| inputs.sn_password | `CHANGE_ME` |

### Project — `ansible-webhooks-to-python-scripts`

Variable: `controller_projects`

| Field | Value |
|-------|--------|
| name | `ansible-webhooks-to-python-scripts` |
| organization | `Default` |
| scm_type | `git` |
| scm_url | `https://github.com/A-Beck/ansible-webhooks-to-python-scripts.git` |
| scm_branch | `main` |
| scm_update_on_launch | `true` |

No SCM credential (public GitHub repo).

### Inventory and host

Variables: `controller_inventories`, `controller_hosts`

| Object | Key fields |
|--------|------------|
| Inventory `Demo Localhost` | organization `Default` |
| Host `localhost` | inventory `Demo Localhost`, variables `ansible_connection: local` |

### Job template — `open_snow_incident`

Variable: `controller_templates` (not `controller_job_templates`)

| Field | Value |
|-------|--------|
| name | `open_snow_incident` |
| organization | `Default` |
| project | `ansible-webhooks-to-python-scripts` |
| playbook | `playbooks/run_snow_incident_script.yml` |
| inventory | `Demo Localhost` |
| credentials | `[ServiceNow Demo]` |
| ask_credential_on_launch | `false` |

## Apply playbook

`setup_aap.yml`:

- hosts: `localhost`, connection local, gather_facts false
- `include_vars` of `aap_vars.yml`
- `include_role: infra.aap_configuration.dispatch`

Dispatch creates objects in dependency order (credential types → credentials → projects → inventories/hosts → templates).

## Dependencies

`collections/requirements.yml` must include at least:

- `infra.aap_configuration`
- `ansible.controller` (and other deps documented by the collection’s getting-started guide for the target AAP version)

## Out of scope

- EDA projects, decision environments, rulebook activations
- Updating `rulebooks/basic_webhook_listener.yml` to call `open_snow_incident` (currently a different JT name)
- Ansible Vault / real ServiceNow secrets
- Custom execution environment
- SCM credentials for private repos

## Success criteria

1. `aap_vars.yml` uses only standard `infra.aap_configuration` list variable names for the objects above
2. `setup_aap.yml` can apply those objects via dispatch when valid AAP auth extra vars are supplied
3. After apply, an operator can launch `open_snow_incident` on Controller; the attached credential injects `SN_*` for the Python script
4. No secrets committed to git
