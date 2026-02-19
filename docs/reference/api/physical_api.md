# physical API Reference

> **Source**: `src/thegent/integration/physical.py`

WP-40001: IoT/Robotics Command Bridge.
Bridges agent logic with physical-world actuators and sensors.
Enables agents to interact with IoT devices or robotic swarms.

---

## physicalWorldBridge

Manages commands sent to physical IoT or robotic devices.

### Methods

#### physicalWorldBridge.__init__

```python
__init__(self, bridge_id)
```

#### physicalWorldBridge.read_sensor

Read telemetry from a physical sensor.

```python
read_sensor(self, device_id, sensor_type)
```

#### physicalWorldBridge.register_device

Register a physical device.

```python
register_device(self, device_id, device_type)
```

#### physicalWorldBridge.send_command

WP-40001: Send an actuation command to a physical device.

```python
send_command(self, device_id, command, params)
```

---

## read_sensor

Read telemetry from a physical sensor.

```python
read_sensor(self, device_id, sensor_type)
```

---

## register_device

Register a physical device.

```python
register_device(self, device_id, device_type)
```

---

## send_command

WP-40001: Send an actuation command to a physical device.

```python
send_command(self, device_id, command, params)
```

---

