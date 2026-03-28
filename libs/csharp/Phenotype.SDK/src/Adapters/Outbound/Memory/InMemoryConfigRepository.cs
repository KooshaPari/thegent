using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.Ports;
using Phenotype.Sdk.Domain.ValueObjects;

namespace Phenotype.Sdk.Adapters.Outbound;

/// <summary>
/// In-memory implementation of IConfigRepository for testing and local development.
/// </summary>
public sealed class InMemoryConfigRepository : IConfigRepository
{
    private readonly Dictionary<string, ConfigEntry> _entries = new();
    private readonly object _lock = new();

    public Task<ConfigEntry?> GetAsync(string key, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (_lock)
        {
            return Task.FromResult(_entries.TryGetValue(key, out var entry) ? entry : null);
        }
    }

    public Task<ConfigEntry> SaveAsync(ConfigEntry entry, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (_lock)
        {
            _entries[entry.Key] = entry;
            return Task.FromResult(entry);
        }
    }

    public Task<bool> DeleteAsync(string key, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (_lock)
        {
            return Task.FromResult(_entries.Remove(key));
        }
    }

    public async IAsyncEnumerable<ConfigEntry> ListAsync(
        string? prefix = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        Dictionary<string, ConfigEntry> snapshot;
        lock (_lock)
        {
            snapshot = new Dictionary<string, ConfigEntry>(_entries);
        }

        foreach (var kvp in snapshot)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (prefix is null || kvp.Key.StartsWith(prefix))
                yield return kvp.Value;
        }
    }

    public void Clear() => _entries.Clear();
}

/// <summary>
/// In-memory implementation of IFeatureRepository for testing and local development.
/// </summary>
public sealed class InMemoryFeatureRepository : IFeatureRepository
{
    private readonly Dictionary<string, FeatureFlag> _flags = new();
    private readonly object _lock = new();

    public Task<FeatureFlag?> GetAsync(string key, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (_lock)
        {
            return Task.FromResult(_flags.TryGetValue(key, out var flag) ? flag : null);
        }
    }

    public Task<FeatureFlag> SaveAsync(FeatureFlag flag, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        lock (_lock)
        {
            _flags[flag.Key] = flag;
            return Task.FromResult(flag);
        }
    }

    public async IAsyncEnumerable<FeatureFlag> ListAsync(
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        Dictionary<string, FeatureFlag> snapshot;
        lock (_lock)
        {
            snapshot = new Dictionary<string, FeatureFlag>(_flags);
        }

        foreach (var kvp in snapshot)
        {
            cancellationToken.ThrowIfCancellationRequested();
            yield return kvp.Value;
        }
    }

    public void Clear() => _flags.Clear();
}
