using Phenotype.Sdk.Domain.Entities;

namespace Phenotype.Sdk.Domain.Ports;

/// <summary>
/// Port interface for configuration persistence.
/// </summary>
/// <remarks>
/// Hexagonal Architecture: Driven/Secondary Port.
/// Defined by the domain, implemented by adapters.
/// </remarks>
public interface IConfigRepository
{
    /// <summary>
    /// Retrieve a configuration entry by key.
    /// </summary>
    Task<ConfigEntry?> GetAsync(string key, CancellationToken cancellationToken = default);

    /// <summary>
    /// Persist a configuration entry.
    /// </summary>
    Task<ConfigEntry> SaveAsync(ConfigEntry entry, CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a configuration entry.
    /// </summary>
    Task<bool> DeleteAsync(string key, CancellationToken cancellationToken = default);

    /// <summary>
    /// List all configuration entries with optional prefix filter.
    /// </summary>
    IAsyncEnumerable<ConfigEntry> ListAsync(string? prefix = null, CancellationToken cancellationToken = default);
}

/// <summary>
/// Port interface for publishing configuration change events.
/// </summary>
public interface IConfigEventPublisher
{
    Task PublishConfigCreatedAsync(ConfigEntry entry, CancellationToken cancellationToken = default);
    Task PublishConfigUpdatedAsync(ConfigEntry entry, ConfigEntry previous, CancellationToken cancellationToken = default);
    Task PublishConfigDeletedAsync(string key, CancellationToken cancellationToken = default);
}

/// <summary>
/// Port interface for feature flag persistence.
/// </summary>
public interface IFeatureRepository
{
    Task<FeatureFlag?> GetAsync(string key, CancellationToken cancellationToken = default);
    Task<FeatureFlag> SaveAsync(FeatureFlag flag, CancellationToken cancellationToken = default);
    IAsyncEnumerable<FeatureFlag> ListAsync(CancellationToken cancellationToken = default);
}

/// <summary>
/// Port interface for feature evaluation strategies.
/// </summary>
public interface IFeatureEvaluator
{
    Task<bool> IsEnabledAsync(string flagKey, string userId, IReadOnlyDictionary<string, object>? attributes = null, CancellationToken cancellationToken = default);
    Task<string?> GetVariantAsync(string flagKey, string userId, IReadOnlyDictionary<string, object>? attributes = null, CancellationToken cancellationToken = default);
}
