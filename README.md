# ansible-webhooks-to-python-scripts

Demo that shows EDA event streams → rulebook activations → a Controller job template that creates a ServiceNow incident via a Python script.

## Rulebooks

Ansible Rulebooks are the foundational element for EDA. They allow the platform to react to events in the environment.

The `rulebooks/` directory contains examples of both single-purpose and multi-purpose events.
- https://docs.ansible.com/projects/rulebook/en/v1.3.2/

 Rulebooks are run by the Ansible Automation Platform Event-Driven Automation Controller:
- https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/administer-assembly_eda_user_guide_overview

## Playbooks

Ansible Playbooks are contain procedural tasks - in our case, launching a script. They are invoked from a rulebook in this example.
- https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html

The `playbooks/run_snow_incident_script.yml` is an example playbook that launches the `scripts/create_snow_incident.py` script.

Playbooks are run by Job Templates in the Ansible Automation Platform Automation Controller:
- https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/develop-assembly_ug_controller_job_templates
