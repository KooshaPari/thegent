# compliance_profile API Reference

> **Source**: `src/thegent/phases/compliance_profile.py`

Compliance profile mapping (EU-AI-ACT, US-SEC, SOX, GDPR).

---

## ComplianceProfile

Compliance profile mapping.

### Methods

#### ComplianceProfile.__init__

```python
__init__(self: Any, profile_name: str)
```

Initialize compliance profile.

**Parameters**:

- `profile_name`: Name of compliance profile

---

#### ComplianceProfile.check_compliance

```python
check_compliance(self: Any, feature: str)
```

Check if a feature is compliant.

**Parameters**:

- `feature`: Feature name

**Returns**: True if compliant

---

#### ComplianceProfile.get_requirements

```python
get_requirements(self: Any)
```

Get requirements for this profile.

**Returns**: List of requirement names

---

---

## check_compliance

```python
check_compliance(self: Any, feature: str)
```

Check if a feature is compliant.

**Parameters**:

- `feature`: Feature name

**Returns**: True if compliant

---

## get_requirements

```python
get_requirements(self: Any)
```

Get requirements for this profile.

**Returns**: List of requirement names

---

## validate_profile_drift

```python
validate_profile_drift(profiles: dict[(str, dict[(str, str)])], required_keys: set[str], allowlist: Any)
```

Validate profile key presence and cross-environment drift.

---

