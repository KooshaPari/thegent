using Phenotype.Sdk.Adapters.Outbound.Memory;
using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.ValueObjects;
using FluentAssertions;

namespace Phenotype.Sdk.Tests.Integration;

public class InMemoryConfigRepositoryTests
{
    private readonly InMemoryConfigRepository _repository;

    public InMemoryConfigRepositoryTests()
    {
        _repository = new InMemoryConfigRepository();
    }

    [Fact]
    public async Task SaveAndGet_ShouldPersistEntry()
    {
        // Arrange
        var entry = ConfigEntry.Create("test.key", "test-value", ValueType.String);

        // Act
        await _repository.SaveAsync(entry);
        var retrieved = await _repository.GetAsync("test.key");

        // Assert
        retrieved.Should().NotBeNull();
        retrieved!.Key.Should().Be("test.key");
        retrieved.Value.Should().Be("test-value");
    }

    [Fact]
    public async Task Delete_ShouldRemoveEntry()
    {
        // Arrange
        var entry = ConfigEntry.Create("to-delete", "value", ValueType.String);
        await _repository.SaveAsync(entry);

        // Act
        var deleted = await _repository.DeleteAsync("to-delete");
        var retrieved = await _repository.GetAsync("to-delete");

        // Assert
        deleted.Should().BeTrue();
        retrieved.Should().BeNull();
    }

    [Fact]
    public async Task List_WithPrefix_ShouldFilterEntries()
    {
        // Arrange
        await _repository.SaveAsync(ConfigEntry.Create("db.host", "localhost", ValueType.String));
        await _repository.SaveAsync(ConfigEntry.Create("db.port", "5432", ValueType.String));
        await _repository.SaveAsync(ConfigEntry.Create("api.key", "secret", ValueType.String));

        // Act
        var dbEntries = new List<ConfigEntry>();
        await foreach (var entry in _repository.ListAsync("db."))
        {
            dbEntries.Add(entry);
        }

        // Assert
        dbEntries.Should().HaveCount(2);
        dbEntries.Select(e => e.Key).Should().BeEquivalentTo(new[] { "db.host", "db.port" });
    }

    [Fact]
    public async Task ConcurrentAccess_ShouldBeThreadSafe()
    {
        // Arrange
        var tasks = Enumerable.Range(0, 100)
            .Select(i => Task.Run(async () =>
            {
                var entry = ConfigEntry.Create($"key-{i}", $"value-{i}", ValueType.String);
                await _repository.SaveAsync(entry);
            }))
            .ToList();

        // Act
        await Task.WhenAll(tasks);

        // Assert
        var count = 0;
        await foreach (var _ in _repository.ListAsync())
        {
            count++;
        }
        count.Should().Be(100);
    }
}
