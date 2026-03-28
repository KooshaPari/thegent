namespace Phenotype.Sdk.Domain.Entities;

/// <summary>
/// Core domain entity representing a configuration entry.
/// </summary>
/// <remarks>
/// Immutable once created. Validation occurs at construction (DDD Entity).
/// </remarks>
public sealed class ConfigEntry
{
    public Guid Id { get; }
    public string Key { get; }
    public string Value { get; }
    public ValueObjects.ValueType ValueType { get; }
    public int Version { get; }
    public DateTime CreatedAt { get; }
    public DateTime UpdatedAt { get; }
    public IReadOnlyDictionary<string, string> Metadata { get; }

    private ConfigEntry(
        Guid id,
        string key,
        string value,
        ValueObjects.ValueType valueType,
        int version,
        DateTime createdAt,
        DateTime updatedAt,
        Dictionary<string, string> metadata)
    {
        Id = id;
        Key = key;
        Value = value;
        ValueType = valueType;
        Version = version;
        CreatedAt = createdAt;
        UpdatedAt = updatedAt;
        Metadata = metadata;
    }

    /// <summary>
    /// Factory method to create a new ConfigEntry with validation.
    /// </summary>
    public static ConfigEntry Create(string key, string value, ValueObjects.ValueType valueType)
    {
        if (string.IsNullOrWhiteSpace(key))
            throw new ArgumentException("Key cannot be empty", nameof(key));
        if (value is null)
            throw new ArgumentNullException(nameof(value));

        // Validate value type
        ValueObjects.ConfigValue.Validate(key, value, valueType);

        return new ConfigEntry(
            id: Guid.NewGuid(),
            key: key,
            value: value,
            valueType: valueType,
            version: 1,
            createdAt: DateTime.UtcNow,
            updatedAt: DateTime.UtcNow,
            metadata: new Dictionary<string, string>());
    }

    /// <summary>
    /// Create a new version with updated value (immutable update pattern).
    /// </summary>
    public ConfigEntry WithUpdatedValue(string newValue)
    {
        ValueObjects.ConfigValue.Validate(Key, newValue, ValueType);

        return new ConfigEntry(
            id: Id,
            key: Key,
            value: newValue,
            valueType: ValueType,
            version: Version + 1,
            createdAt: CreatedAt,
            updatedAt: DateTime.UtcNow,
            metadata: new Dictionary<string, string>(Metadata));
    }

    /// <summary>
    /// Add or update metadata (returns new instance).
    /// </summary>
    public ConfigEntry WithMetadata(string key, string value)
    {
        var newMetadata = new Dictionary<string, string>(Metadata) { [key] = value };
        return new ConfigEntry(
            id: Id,
            key: Key,
            value: Value,
            valueType: ValueType,
            version: Version,
            createdAt: CreatedAt,
            updatedAt: DateTime.UtcNow,
            metadata: newMetadata);
    }
}

/// <summary>
/// Core domain entity representing a feature flag.
/// </summary>
public sealed class FeatureFlag
{
    public Guid Id { get; }
    public string Key { get; }
    public bool Enabled { get; }
    public double RolloutPercentage { get; }
    public IReadOnlyList<TargetingRule> TargetingRules { get; }
    public DateTime CreatedAt { get; }
    public DateTime UpdatedAt { get; }

    private FeatureFlag(
        Guid id,
        string key,
        bool enabled,
        double rolloutPercentage,
        List<TargetingRule> targetingRules,
        DateTime createdAt,
        DateTime updatedAt)
    {
        Id = id;
        Key = key;
        Enabled = enabled;
        RolloutPercentage = rolloutPercentage;
        TargetingRules = targetingRules;
        CreatedAt = createdAt;
        UpdatedAt = updatedAt;
    }

    /// <summary>
    /// Factory method to create a new FeatureFlag.
    /// </summary>
    public static FeatureFlag Create(string key, bool enabled, double rolloutPercentage = 100.0)
    {
        if (string.IsNullOrWhiteSpace(key))
            throw new ArgumentException("Key cannot be empty", nameof(key));
        if (rolloutPercentage < 0 || rolloutPercentage > 100)
            throw new ArgumentOutOfRangeException(nameof(rolloutPercentage));

        return new FeatureFlag(
            id: Guid.NewGuid(),
            key: key,
            enabled: enabled,
            rolloutPercentage: rolloutPercentage,
            targetingRules: new List<TargetingRule>(),
            createdAt: DateTime.UtcNow,
            updatedAt: DateTime.UtcNow);
    }

    /// <summary>
    /// Determine if feature is enabled for a specific user.
    /// </summary>
    public bool IsEnabledForUser(string userId, IReadOnlyDictionary<string, object>? attributes = null)
    {
        if (!Enabled) return false;
        if (string.IsNullOrEmpty(userId)) return false;

        // Check targeting rules first
        foreach (var rule in TargetingRules)
        {
            if (rule.Evaluate(attributes))
                return true;
        }

        // Fall back to percentage rollout
        return CheckPercentageRollout(userId);
    }

    private bool CheckPercentageRollout(string userId)
    {
        // Consistent hashing for stable percentage assignment
        var hash = $"{Key}:{userId}".GetHashCode();
        var bucket = Math.Abs(hash) % 100;
        return bucket < RolloutPercentage;
    }
}

/// <summary>
/// Targeting rule for feature flags.
/// </summary>
public sealed class TargetingRule
{
    public string Attribute { get; }
    public string Operator { get; }
    public object Value { get; }

    public TargetingRule(string attribute, string op, object value)
    {
        Attribute = attribute;
        Operator = op;
        Value = value;
    }

    public bool Evaluate(IReadOnlyDictionary<string, object>? attributes)
    {
        if (attributes is null || !attributes.TryGetValue(Attribute, out var attrValue))
            return false;

        return Operator switch
        {
            "eq" => Equals(attrValue, Value),
            "ne" => !Equals(attrValue, Value),
            "gt" => Compare(attrValue) > 0 && Equals(CompareBase(Value), 0),
            "gte" => Compare(attrValue) >= 0,
            "lt" => Compare(attrValue) < 0,
            "lte" => Compare(attrValue) <= 0,
            "in" => Value is IEnumerable<object> values && values.Contains(attrValue),
            _ => false
        };
    }

    private int Compare(object other) => other switch
    {
        IComparable<int> i => i.CompareTo(Convert.ToInt32(Value)),
        IComparable<double> d => d.CompareTo(Convert.ToDouble(Value)),
        IComparable<string> s => s.CompareTo(Value.ToString()),
        _ => 0
    };

    private static int CompareBase(object value) => value switch
    {
        IComparable<int> i => i.CompareTo(0),
        IComparable<double> d => d.CompareTo(0),
        _ => 0
    };
}
