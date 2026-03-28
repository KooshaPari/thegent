using System.Net.Http.Json;
using System.Text.Json;
using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.Ports;
using Phenotype.Sdk.Domain.ValueObjects;

namespace Phenotype.Sdk.Adapters.Outbound.Http;

/// <summary>
/// HTTP adapter for remote configuration service.
/// </summary>
public sealed class HttpConfigRepository : IConfigRepository, IAsyncDisposable
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    private readonly JsonSerializerOptions _jsonOptions;

    public HttpConfigRepository(HttpClient httpClient, string baseUrl)
    {
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _baseUrl = baseUrl.TrimEnd('/');
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            PropertyNameCaseInsensitive = true
        };
    }

    public async Task<ConfigEntry?> GetAsync(string key, CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.GetAsync(
            $"{_baseUrl}/api/v1/config/{Uri.EscapeDataString(key)}",
            cancellationToken);

        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        var data = await response.Content.ReadFromJsonAsync<ConfigEntryData>(cancellationToken);
        return data is null ? null : FromData(data);
    }

    public async Task<ConfigEntry> SaveAsync(ConfigEntry entry, CancellationToken cancellationToken = default)
    {
        var content = JsonContent.Create(ToData(entry));
        var response = await _httpClient.PostAsync(
            $"{_baseUrl}/api/v1/config",
            content,
            cancellationToken);

        response.EnsureSuccessStatusCode();
        var data = await response.Content.ReadFromJsonAsync<ConfigEntryData>(cancellationToken);
        return data is null ? entry : FromData(data);
    }

    public async Task<bool> DeleteAsync(string key, CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.DeleteAsync(
            $"{_baseUrl}/api/v1/config/{Uri.EscapeDataString(key)}",
            cancellationToken);

        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
            return false;

        response.EnsureSuccessStatusCode();
        return true;
    }

    public async IAsyncEnumerable<ConfigEntry> ListAsync(
        string? prefix = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var url = $"{_baseUrl}/api/v1/config";
        if (prefix is not null)
            url += $"?prefix={Uri.EscapeDataString(prefix)}";

        var response = await _httpClient.GetAsync(url, cancellationToken);
        response.EnsureSuccessStatusCode();

        var data = await response.Content.ReadFromJsonAsync<List<ConfigEntryData>>(cancellationToken);
        if (data is null) yield break;

        foreach (var item in data)
            yield return FromData(item);
    }

    public async ValueTask DisposeAsync() => _httpClient.Dispose();

    private ConfigEntry FromData(ConfigEntryData data) =>
        ConfigEntry.Create(data.Key, data.Value, Enum.Parse<ValueType>(data.ValueType, ignoreCase: true))
            .WithMetadata("id", data.Id);

    private static ConfigEntryData ToData(ConfigEntry entry) => new()
    {
        Id = entry.Id.ToString(),
        Key = entry.Key,
        Value = entry.Value,
        ValueType = entry.ValueType.ToString().ToLowerInvariant(),
        Version = entry.Version,
        Metadata = entry.Metadata
    };

    private sealed class ConfigEntryData
    {
        public string Id { get; set; } = string.Empty;
        public string Key { get; set; } = string.Empty;
        public string Value { get; set; } = string.Empty;
        public string ValueType { get; set; } = string.Empty;
        public int Version { get; set; }
        public Dictionary<string, string> Metadata { get; set; } = new();
    }
}
