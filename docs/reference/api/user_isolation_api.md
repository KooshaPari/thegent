# user_isolation API Reference

> **Source**: `src/thegent/cross_platform/user_isolation.py`

System User abstraction for cross-platform agent execution.

This module provides SystemUser and AgentUser classes that abstract
the distinction between system-level and agent-level user contexts
for secure cross-platform operation.

---

## AgentUser

Agent-level user context for isolated agent execution.

Represents the user context under which agents operate, providing
isolation from the host system user and ensuring secure, controlled
execution environment.

**Inherits from**: `UserContext`

**Method Resolution Order**: `AgentUser -> UserContext`

### Methods

#### AgentUser.__init__

```python
__init__(self: Any, agent_id: Any, agent_home: Any)
```

Initialize agent user context.

**Parameters**:

- `agent_id`: Unique identifier for the agent
- `agent_home`: Custom home directory for the agent (defaults to temp)

---

#### AgentUser.can_access_path

```python
can_access_path(self: Any, path: Path)
```

Check if agent can access a given path.

Agents are typically restricted to their home directory and
any explicitly granted paths.

---

#### AgentUser.get_environment_vars

```python
get_environment_vars(self: Any)
```

Get filtered environment variables for agent.

Returns a sanitized set of environment variables suitable
for agent execution.

---

#### AgentUser.home_dir

```python
home_dir(self: Any)
```

Return the agent's home directory.

---

#### AgentUser.is_privileged

```python
is_privileged(self: Any)
```

Check if agent has elevated privileges (typically false).

---

#### AgentUser.user_id

```python
user_id(self: Any)
```

Return the agent's user ID (same as host user).

---

#### AgentUser.user_name

```python
user_name(self: Any)
```

Return the agent username.

---

---

## SystemUser

System-level user context (root/sudo on Unix, Administrator on Windows).

Used for system-wide installations, global configuration, and
administrative tasks that require elevated privileges.

**Inherits from**: `UserContext`

**Method Resolution Order**: `SystemUser -> UserContext`

### Methods

#### SystemUser.__init__

```python
__init__(self: Any)
```

Initialize system user context.

---

#### SystemUser.can_access_path

```python
can_access_path(self: Any, path: Path)
```

System user can access any path (if permissions allow).

---

#### SystemUser.get_environment_vars

```python
get_environment_vars(self: Any)
```

Get system environment variables.

---

#### SystemUser.home_dir

```python
home_dir(self: Any)
```

Return system directories.

---

#### SystemUser.is_privileged

```python
is_privileged(self: Any)
```

Check if running with elevated privileges.

---

#### SystemUser.user_id

```python
user_id(self: Any)
```

Return the user ID (0 for root).

---

#### SystemUser.user_name

```python
user_name(self: Any)
```

Return the username (root or SYSTEM on Windows).

---

---

## UserContext

Abstract base class for user contexts.

**Inherits from**: `ABC`

### Methods

#### UserContext.can_access_path

```python
can_access_path(self: Any, path: Path)
```

Check if user can access a given path.

---

#### UserContext.get_environment_vars

```python
get_environment_vars(self: Any)
```

Get environment variables visible to this user.

---

#### UserContext.home_dir

```python
home_dir(self: Any)
```

Return the home directory.

---

#### UserContext.is_privileged

```python
is_privileged(self: Any)
```

Check if running with elevated privileges.

---

#### UserContext.user_id

```python
user_id(self: Any)
```

Return the user ID.

---

#### UserContext.user_name

```python
user_name(self: Any)
```

Return the username.

---

---

## can_access_path

```python
can_access_path(self: Any, path: Path)
```

Check if agent can access a given path.

Agents are typically restricted to their home directory and
any explicitly granted paths.

---

## get_environment_vars

```python
get_environment_vars(self: Any)
```

Get filtered environment variables for agent.

Returns a sanitized set of environment variables suitable
for agent execution.

---

## get_user_context

```python
get_user_context(context_type: str)
```

Factory function to get a user context.

**Parameters**:

- `context_type`: Type of context ('system' or 'agent')
- `**kwargs`: Additional arguments passed to context constructor

**Returns**: UserContext instance

**Raises**:

- `ValueError`: If context_type is invalid

---

## home_dir

```python
home_dir(self: Any)
```

Return the agent's home directory.

---

## is_privileged

```python
is_privileged(self: Any)
```

Check if agent has elevated privileges (typically false).

---

## user_id

```python
user_id(self: Any)
```

Return the agent's user ID (same as host user).

---

## user_name

```python
user_name(self: Any)
```

Return the agent username.

---

