using Phenotype.Sdk.Application.DTO;
using Phenotype.Sdk.Application.UseCases;
using Phenotype.Sdk.Domain.Entities;
using Phenotype.Sdk.Domain.Ports;
using Phenotype.Sdk.Domain.ValueObjects;
using FluentAssertions;
using Moq;

namespace Phenotype.Sdk.Tests.Unit;

public class ConfigUseCasesTests
{
    private readonly Mock<IConfigRepository> _repositoryMock;
    private readonly Mock<IConfigEventPublisher> _publisherMock;
    private readonly ConfigUseCases _useCases;

    public ConfigUseCasesTests()
    {
        _repositoryMock = new Mock<IConfigRepository>();
        _publisherMock = new Mock<IConfigEventPublisher>();
        _useCases = new ConfigUseCases(_repositoryMock.Object, _publisherMock.Object);
    }

    [Fact]
    public async Task CreateConfig_WithValidData_ShouldCreateAndPublishEvent()
    {
        // Arrange
        var dto = new CreateConfigDTO("database.host", "localhost", ValueType.String);

        _repositoryMock.Setup(r => r.GetAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((ConfigEntry?)null);

        _repositoryMock.Setup(r => r.SaveAsync(It.IsAny<ConfigEntry>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((ConfigEntry e, CancellationToken _) => e);

        // Act
        var result = await _useCases.CreateConfigAsync(dto);

        // Assert
        result.Should().NotBeNull();
        result.Key.Should().Be("database.host");
        result.Value.Should().Be("localhost");
        result.ValueType.Should().Be(ValueType.String);
        result.Version.Should().Be(1);

        _publisherMock.Verify(
            p => p.PublishConfigCreatedAsync(It.IsAny<ConfigEntry>(), It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task CreateConfig_WithExistingKey_ShouldThrowException()
    {
        // Arrange
        var existing = ConfigEntry.Create("database.host", "old-value", ValueType.String);
        var dto = new CreateConfigDTO("database.host", "new-value", ValueType.String);

        _repositoryMock.Setup(r => r.GetAsync("database.host", It.IsAny<CancellationToken>()))
            .ReturnsAsync(existing);

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _useCases.CreateConfigAsync(dto));
    }

    [Fact]
    public async Task UpdateConfig_WithExistingKey_ShouldUpdateAndPublishEvent()
    {
        // Arrange
        var existing = ConfigEntry.Create("database.host", "localhost", ValueType.String);
        var dto = new UpdateConfigDTO("database.host", "127.0.0.1");

        _repositoryMock.Setup(r => r.GetAsync("database.host", It.IsAny<CancellationToken>()))
            .ReturnsAsync(existing);

        _repositoryMock.Setup(r => r.SaveAsync(It.IsAny<ConfigEntry>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((ConfigEntry e, CancellationToken _) => e);

        // Act
        var result = await _useCases.UpdateConfigAsync(dto);

        // Assert
        result.Value.Should().Be("127.0.0.1");
        result.Version.Should().Be(2);

        _publisherMock.Verify(
            p => p.PublishConfigUpdatedAsync(
                It.IsAny<ConfigEntry>(),
                It.Is<ConfigEntry>(e => e.Value == "localhost"),
                It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task GetConfig_WithNonExistentKey_ShouldThrowKeyNotFoundException()
    {
        // Arrange
        _repositoryMock.Setup(r => r.GetAsync("nonexistent", It.IsAny<CancellationToken>()))
            .ReturnsAsync((ConfigEntry?)null);

        // Act & Assert
        await Assert.ThrowsAsync<KeyNotFoundException>(
            () => _useCases.GetConfigAsync("nonexistent"));
    }
}

public class ConfigEntryTests
{
    [Fact]
    public void Create_WithValidData_ShouldCreateEntry()
    {
        // Act
        var entry = ConfigEntry.Create("test.key", "test-value", ValueType.String);

        // Assert
        entry.Key.Should().Be("test.key");
        entry.Value.Should().Be("test-value");
        entry.ValueType.Should().Be(ValueType.String);
        entry.Version.Should().Be(1);
        entry.Id.Should().NotBeEmpty();
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public void Create_WithEmptyKey_ShouldThrowArgumentException(string? key)
    {
        // Act & Assert
        Assert.Throws<ArgumentException>(() => ConfigEntry.Create(key!, "value", ValueType.String));
    }

    [Fact]
    public void WithUpdatedValue_ShouldIncrementVersion()
    {
        // Arrange
        var entry = ConfigEntry.Create("test.key", "v1", ValueType.String);

        // Act
        var updated = entry.WithUpdatedValue("v2");

        // Assert
        updated.Value.Should().Be("v2");
        updated.Version.Should().Be(2);
        updated.Id.Should().Be(entry.Id); // Same identity
    }
}

public class FeatureFlagTests
{
    [Fact]
    public void Create_WithValidData_ShouldCreateFlag()
    {
        // Act
        var flag = FeatureFlag.Create("new-feature", true, 50.0);

        // Assert
        flag.Key.Should().Be("new-feature");
        flag.Enabled.Should().BeTrue();
        flag.RolloutPercentage.Should().Be(50.0);
    }

    [Fact]
    public void IsEnabledForUser_WhenDisabled_ShouldReturnFalse()
    {
        // Arrange
        var flag = FeatureFlag.Create("disabled-feature", false, 100.0);

        // Act
        var result = flag.IsEnabledForUser("user-123");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void IsEnabledForUser_When100Percent_ShouldReturnTrue()
    {
        // Arrange
        var flag = FeatureFlag.Create("enabled-feature", true, 100.0);

        // Act & Assert - Multiple users should all get true
        for (int i = 0; i < 100; i++)
        {
            flag.IsEnabledForUser($"user-{i}").Should().BeTrue();
        }
    }

    [Fact]
    public void IsEnabledForUser_When0Percent_ShouldReturnFalse()
    {
        // Arrange
        var flag = FeatureFlag.Create("zero-feature", true, 0.0);

        // Act & Assert - Multiple users should all get false
        for (int i = 0; i < 100; i++)
        {
            flag.IsEnabledForUser($"user-{i}").Should().BeFalse();
        }
    }
}
