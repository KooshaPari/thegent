// Auto-generated usage examples for physical
// Source: generate-api-docs.py

import { physicalWorldBridge, read_sensor, register_device, send_command } from "./physical";

// Create a physicalWorldBridge instance
const physicalworldbridge = new physicalWorldBridge("example_bridge_id");
physicalworldbridge.read_sensor("example_device_id", "example_sensor_type");
physicalworldbridge.register_device("example_device_id", "example_device_type");
physicalworldbridge.send_command("example_device_id", "example_command", undefined as unknown as Record<(str, Any)>);

// Call read_sensor
read_sensor(undefined as unknown as any, "example_device_id", "example_sensor_type");
// Call register_device
register_device(undefined as unknown as any, "example_device_id", "example_device_type");
// Call send_command
send_command(undefined as unknown as any, "example_device_id", "example_command", undefined as unknown as Record<(str, Any)>);
