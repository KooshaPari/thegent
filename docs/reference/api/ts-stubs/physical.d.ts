// Auto-generated TypeScript declarations for physical
// Source: generate-api-docs.py

export declare class physicalWorldBridge {
  constructor(bridge_id: string);
  read_sensor(device_id: string, sensor_type: string): void;
  register_device(device_id: string, device_type: string): void;
  send_command(device_id: string, command: string, params: Record<(str, Any)>): void;
}

export declare function read_sensor(device_id: string, sensor_type: string): void;
export declare function register_device(device_id: string, device_type: string): void;
export declare function send_command(device_id: string, command: string, params: Record<(str, Any)>): void;
