# provisioner API Reference

> **Source**: `src/thegent/infra/provisioner.py`

WP-31001: Self-Provisioning Infra Bridge.
Enables agents to provision their own compute, storage, and networking resources.
Provides a high-level API over Terraform/Cloud-init/Docker.

---

## InfraProvisioner

Orchestrates self-provisioning of agent infrastructure.

### Methods

#### InfraProvisioner.__init__

```python
__init__(self, provider)
```

#### InfraProvisioner.decommission

Release a previously provisioned resource.

```python
decommission(self, resource_id)
```

#### InfraProvisioner.provision

Provision a resource based on the spec.

```python
provision(self, resource_id, spec)
```

---

## ResourceSpec

Specification for an infra resource.

**Inherits from**: `BaseModel`

---

## decommission

Release a previously provisioned resource.

```python
decommission(self, resource_id)
```

---

## provision

Provision a resource based on the spec.

```python
provision(self, resource_id, spec)
```

---

