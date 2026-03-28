# Infrastructure

Infrastructure-as-Code and deployment configurations for the Phenotype ecosystem.

## Overview

This directory contains infrastructure definitions for:
- Cloud deployments
- Kubernetes manifests
- Terraform configurations
- Ansible playbooks

## Directory Structure

```
infrastructure/
├── terraform/         # Terraform configurations
├── kubernetes/        # Kubernetes manifests and Helm charts
└── ansible/           # Ansible playbooks
```

## Terraform

Infrastructure provisioning for cloud resources.

```
infrastructure/terraform/
├── modules/           # Reusable Terraform modules
├── environments/      # Environment-specific configs
│   ├── dev/
│   ├── staging/
│   └── prod/
└── main.tf            # Root configuration
```

## Kubernetes

Container orchestration manifests.

```
infrastructure/kubernetes/
├── base/              # Base k8s manifests
├── overlays/           # Environment overlays
└── helm/              # Helm chart templates
```

## Ansible

Configuration management and automation.

```
infrastructure/ansible/
├── roles/             # Ansible roles
├── playbooks/         # Playbook definitions
└── inventory/          # Inventory files
```

## Usage

### Terraform

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Kubernetes

```bash
kubectl apply -k infrastructure/kubernetes/overlays/dev
```

### Ansible

```bash
ansible-playbook -i infrastructure/ansible/inventory/prod.ini infrastructure/ansible/playbooks/deploy.yml
```

## References

- [ADR-0005: Top-Level Directory Structure](../governance/adrs/0005-top-level-directory-structure.md)
