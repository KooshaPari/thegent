namespace Phenotype.Sdk.Domain.ValueObjects;

/// <summary>
/// Enumeration of supported configuration value types.
/// </summary>
public enum ValueType
{
    String,
    Integer,
    Float,
    Boolean,
    Json,
    Secret
}

/// <summary>
/// Value object representing a validated configuration value.
/// </summary>
/// <remarks>
/// Immutable and validated at construction time (DDD Value Object pattern).
/// </remarks>
public sealed class ConfigValue
{
    public string Raw { get; }
    public ValueType ValueType { get; }

    private ConfigValue(string raw, ValueType valueType)
    {
        Raw = raw;
        ValueType = valueType;
    }

    /// <summary>
    /// Create a validated ConfigValue.
    /// </summary>
    public static ConfigValue Create(string raw, ValueType valueType)
    {
        Validate(raw, valueType);
        return new ConfigValue(raw, valueType);
    }

    /// <summary>
    /// Validate that the raw value matches the declared type.
    /// </summary>
    internal static void Validate(string raw, ValueType valueType)
    {
        ArgumentNullException.ThrowIfNull(raw);

        switch (valueType)
        {
            case ValueType.String:
                // Strings are always valid
                break;

            case ValueType.Integer:
                if (!long.TryParse(raw, out _))
                    throw new FormatException($"Expected integer value, got: {raw}");
                break;

            case ValueType.Float:
                if (!double.TryParse(raw, out _))
                    throw new FormatException($"Expected float value, got: {raw}");
                break;

            case ValueType.Boolean:
                if (!bool.TryParse(raw, out _) && raw != "1" && raw != "0")
                    throw new FormatException($"Expected boolean value, got: {raw}");
                break;

            case ValueType.Json:
                // Basic JSON validation
                if (raw.TrimStart().FirstOrDefault() is not ('{' or '['))
                    throw new FormatException($"Expected JSON object or array, got: {raw}");
                break;

            case ValueType.Secret:
                // Secrets are strings but should be handled specially
                break;

            default:
                throw new ArgumentOutOfRangeException(nameof(valueType));
        }
    }

    /// <summary>
    /// Get the typed value as the appropriate .NET type.
    /// </summary>
    public object GetTypedValue() => ValueType switch
    {
        ValueType.String => Raw,
        ValueType.Integer => long.Parse(Raw),
        ValueType.Float => double.Parse(Raw),
        ValueType.Boolean => bool.Parse(Raw),
        ValueType.Json => Raw, // Would deserialize in production
        ValueType.Secret => Raw,
        _ => Raw
    };
}

/// <summary>
/// Specialized value object for secrets with masking.
/// </summary>
public sealed class SecretValue : ConfigValue
{
    public SecretValue(string raw) : base(raw, ValueType.Secret) { }

    public string Reveal() => Raw;

    public override string ToString() => "***REDACTED***";
}
