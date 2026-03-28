# routing_dashboard API Reference

> **Source**: `src/thegent/tui/routing_dashboard.py`

Routing and Cost Dashboard TUI component.

---

## RoutingDashboard

Routing dashboard component.

**Inherits from**: `Vertical`

### Methods

#### RoutingDashboard.compose

```python
compose(self: Any)
```

Compose the routing dashboard.

---

#### RoutingDashboard.on_mount

```python
on_mount(self: Any)
```

Initialize on mount.

---

#### RoutingDashboard.refresh_data

```python
refresh_data(self: Any)
```

Refresh routing data.

---

---

## RoutingStatsPanel

Statistics panel showing routing metrics.

**Inherits from**: `Static`

### Methods

#### RoutingStatsPanel.__init__

```python
__init__(self: Any)
```

---

#### RoutingStatsPanel.update_stats

```python
update_stats(self: Any, stats: dict[(str, Any)])
```

Update statistics display.

---

---

## RoutingTable

Table showing recent routing events.

**Inherits from**: `DataTable`

### Methods

#### RoutingTable.__init__

```python
__init__(self: Any)
```

---

#### RoutingTable.update_entries

```python
update_entries(self: Any, entries: list[dict[(str, Any)]])
```

Update routing table.

---

---

## compose

```python
compose(self: Any)
```

Compose the routing dashboard.

---

## on_mount

```python
on_mount(self: Any)
```

Initialize on mount.

---

## refresh_data

```python
refresh_data(self: Any)
```

Refresh routing data.

---

## update_entries

```python
update_entries(self: Any, entries: list[dict[(str, Any)]])
```

Update routing table.

---

## update_stats

```python
update_stats(self: Any, stats: dict[(str, Any)])
```

Update statistics display.

---

