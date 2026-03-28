namespace Phenotype.Sdk;

/// <summary>
/// Phenotype SDK - Configuration management SDK.
/// </summary>
public static class PhenotypeSdk
{
    /// <summary>
    /// SDK version.
    /// </summary>
    public const string Version = "0.1.0";
}

/// <summary>
/// Domain layer - Pure business logic with no external dependencies.
/// </summary>
public static class PhenotypeDomain
{
    public static Type ConfigEntry => typeof(Domain.Entities.ConfigEntry);
    public static Type FeatureFlag => typeof(Domain.Entities.FeatureFlag);
    public static Type ConfigValue => typeof(Domain.ValueObjects.ConfigValue);
    public static Type ConfigRepository => typeof(Domain.Ports.IConfigRepository);
    public static Type FeatureRepository => typeof(Domain.Ports.IFeatureRepository);
}

/// <summary>
/// Application layer - Use cases and orchestration.
/// </summary>
public static class PhenotypeApplication
{
    public static Type ConfigUseCases => typeof(Application.UseCases.ConfigUseCases);
    public static Type FeatureUseCases => typeof(Application.UseCases.FeatureUseCases);
}

/// <summary>
/// Adapters layer - Infrastructure implementations.
/// </summary>
public static class PhenotypeAdapters
{
    public static Type InMemoryConfigRepository => typeof(Adapters.Outbound.Memory.InMemoryConfigRepository);
    public static Type InMemoryFeatureRepository => typeof(Adapters.Outbound.Memory.InMemoryFeatureRepository);
    public static Type HttpConfigRepository => typeof(Adapters.Outbound.Http.HttpConfigRepository);
}
