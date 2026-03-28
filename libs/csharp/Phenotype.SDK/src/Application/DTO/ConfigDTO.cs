using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.ValueObjects;

namespace Phenotype.Sdk.Application.DTO;

/// <summary>
/// DTO for creating a new configuration entry.
/// </summary>
public sealed record CreateConfigDTO(
    string Key,
    string Value,
    ValueType ValueType,
    IReadOnlyDictionary<string, string>? Metadata = null);

/// <summary>
/// DTO for updating a configuration entry.
/// </summary>
public sealed record UpdateConfigDTO(
    string Key,
    string Value);

/// <summary>
/// DTO for configuration entry responses.
/// </summary>
public sealed record ConfigEntryDTO(
    string Id,
    string Key,
    string Value,
    ValueType ValueType,
    int Version,
    DateTime CreatedAt,
    DateTime UpdatedAt,
    IReadOnlyDictionary<string, string>? Metadata = null)
{
    public static ConfigEntryDTO FromEntity(ConfigEntry entity) =>
        new(
            Id: entity.Id.ToString(),
            Key: entity.Key,
            Value: entity.Value,
            ValueType: entity.ValueType,
            Version: entity.Version,
            CreatedAt: entity.CreatedAt,
            UpdatedAt: entity.UpdatedAt,
            Metadata: entity.Metadata);
}

/// <summary>
/// DTO for creating a feature flag.
/// </summary>
public sealed record CreateFeatureFlagDTO(
    string Key,
    bool Enabled,
    double RolloutPercentage = 100.0);

/// <summary>
/// DTO for feature flag responses.
/// </summary>
public sealed record FeatureFlagDTO(
    string Id,
    string Key,
    bool Enabled,
    double RolloutPercentage,
    DateTime CreatedAt,
    DateTime UpdatedAt)
{
    public static FeatureFlagDTO FromEntity(FeatureFlag entity) =>
        new(
            Id: entity.Id.ToString(),
            Key: entity.Key,
            Enabled: entity.Enabled,
            RolloutPercentage: entity.RolloutPercentage,
            CreatedAt: entity.CreatedAt,
            UpdatedAt: entity.UpdatedAt);
}
