using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.Ports;
using Phenotype.Sdk.Domain.ValueObjects;

namespace Phenotype.Sdk.Application.UseCases;

/// <summary>
/// Application service for configuration management.
/// </summary>
/// <remarks>
/// Orchestrates domain entities and ports (Application Service pattern).
/// Handles cross-cutting concerns like validation and event publishing.
/// </remarks>
public class ConfigUseCases
{
    private readonly IConfigRepository _repository;
    private readonly IConfigEventPublisher? _eventPublisher;

    public ConfigUseCases(IConfigRepository repository, IConfigEventPublisher? eventPublisher = null)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _eventPublisher = eventPublisher;
    }

    /// <summary>
    /// Create a new configuration entry.
    /// </summary>
    public async Task<ConfigEntry> CreateConfigAsync(
        DTO.CreateConfigDTO dto,
        CancellationToken cancellationToken = default)
    {
        // Check for existing entry
        var existing = await _repository.GetAsync(dto.Key, cancellationToken);
        if (existing is not null)
            throw new InvalidOperationException($"Config entry already exists: {dto.Key}");

        // Create domain entity
        var entry = ConfigEntry.Create(dto.Key, dto.Value, dto.ValueType);

        // Apply metadata if provided
        if (dto.Metadata is not null)
        {
            foreach (var kvp in dto.Metadata)
            {
                entry = entry.WithMetadata(kvp.Key, kvp.Value);
            }
        }

        // Persist
        var saved = await _repository.SaveAsync(entry, cancellationToken);

        // Publish event (CQRS: separate read/write models)
        if (_eventPublisher is not null)
            await _eventPublisher.PublishConfigCreatedAsync(saved, cancellationToken);

        return saved;
    }

    /// <summary>
    /// Update an existing configuration entry.
    /// </summary>
    public async Task<ConfigEntry> UpdateConfigAsync(
        DTO.UpdateConfigDTO dto,
        CancellationToken cancellationToken = default)
    {
        var existing = await _repository.GetAsync(dto.Key, cancellationToken)
            ?? throw new KeyNotFoundException($"Config entry not found: {dto.Key}");

        // Create new version
        var updated = existing.WithUpdatedValue(dto.Value);

        // Persist
        var saved = await _repository.SaveAsync(updated, cancellationToken);

        // Publish event
        if (_eventPublisher is not null)
            await _eventPublisher.PublishConfigUpdatedAsync(saved, existing, cancellationToken);

        return saved;
    }

    /// <summary>
    /// Get a configuration entry.
    /// </summary>
    public async Task<ConfigEntry> GetConfigAsync(
        string key,
        CancellationToken cancellationToken = default)
    {
        var entry = await _repository.GetAsync(key, cancellationToken)
            ?? throw new KeyNotFoundException($"Config entry not found: {key}");
        return entry;
    }

    /// <summary>
    /// Delete a configuration entry.
    /// </summary>
    public async Task<bool> DeleteConfigAsync(
        string key,
        CancellationToken cancellationToken = default)
    {
        var deleted = await _repository.DeleteAsync(key, cancellationToken);

        if (deleted && _eventPublisher is not null)
            await _eventPublisher.PublishConfigDeletedAsync(key, cancellationToken);

        return deleted;
    }

    /// <summary>
    /// List all configuration entries.
    /// </summary>
    public IAsyncEnumerable<ConfigEntry> ListConfigsAsync(
        string? prefix = null,
        CancellationToken cancellationToken = default)
    {
        return _repository.ListAsync(prefix, cancellationToken);
    }
}

/// <summary>
/// Application service for feature flag management.
/// </summary>
public class FeatureUseCases
{
    private readonly IFeatureRepository _repository;

    public FeatureUseCases(IFeatureRepository repository)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
    }

    /// <summary>
    /// Create a new feature flag.
    /// </summary>
    public async Task<FeatureFlag> CreateFlagAsync(
        DTO.CreateFeatureFlagDTO dto,
        CancellationToken cancellationToken = default)
    {
        var flag = FeatureFlag.Create(dto.Key, dto.Enabled, dto.RolloutPercentage);
        return await _repository.SaveAsync(flag, cancellationToken);
    }

    /// <summary>
    /// Get a feature flag.
    /// </summary>
    public async Task<FeatureFlag> GetFlagAsync(
        string key,
        CancellationToken cancellationToken = default)
    {
        var flag = await _repository.GetAsync(key, cancellationToken)
            ?? throw new KeyNotFoundException($"Feature flag not found: {key}");
        return flag;
    }

    /// <summary>
    /// Evaluate if a feature is enabled for a user.
    /// </summary>
    public async Task<bool> EvaluateFlagAsync(
        string key,
        string userId,
        IReadOnlyDictionary<string, object>? attributes = null,
        CancellationToken cancellationToken = default)
    {
        var flag = await GetFlagAsync(key, cancellationToken);
        return flag.IsEnabledForUser(userId, attributes);
    }

    /// <summary>
    /// List all feature flags.
    /// </summary>
    public IAsyncEnumerable<FeatureFlag> ListFlagsAsync(
        CancellationToken cancellationToken = default)
    {
        return _repository.ListAsync(cancellationToken);
    }
}
