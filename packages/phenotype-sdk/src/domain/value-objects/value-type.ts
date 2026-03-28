/**
 * Value type enumeration for configuration values.
 */

export type ValueType = 'string' | 'number' | 'boolean' | 'json' | 'base64';

/**
 * Validate a value against its type.
 */
export function validateValue(value: string, type: ValueType): boolean {
  switch (type) {
    case 'string':
      return true; // Any string is valid

    case 'number':
      return !isNaN(Number(value));

    case 'boolean':
      return ['true', 'false', '0', '1'].includes(value.toLowerCase());

    case 'json':
      try {
        JSON.parse(value);
        return true;
      } catch {
        return false;
      }

    case 'base64':
      return isValidBase64(value);

    default:
      return false;
  }
}

/**
 * Check if a string is valid base64.
 */
function isValidBase64(str: string): boolean {
  if (str.length === 0) return false;
  // Base64 regex: alphanumeric, +, /, = for padding
  return /^[A-Za-z0-9+/]*={0,2}$/.test(str);
}

/**
 * Convert a value to its typed representation.
 */
export function parseValue(value: string, type: ValueType): string | number | boolean | unknown {
  switch (type) {
    case 'string':
      return value;

    case 'number':
      return Number(value);

    case 'boolean':
      return value.toLowerCase() === 'true' || value === '1';

    case 'json':
      return JSON.parse(value);

    case 'base64':
      return value; // Return as-is, let caller decode

    default:
      throw new Error(`Unknown value type: ${type}`);
  }
}
