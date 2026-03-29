import type {
  AwsCreds,
  InstanceRecord,
  InstanceResource,
  LLMConfig,
  LLMProvider,
  NormalizedInstanceRecord,
  NormalizedUser,
  Portfolio,
  User
} from './types';

function toAwsCreds(raw?: AwsCreds | { AccessKeyID?: string; SecretAccessKey?: string }): AwsCreds | undefined {
  if (!raw) return undefined;
  if ('accessKeyId' in raw || 'secretAccessKey' in raw) {
    return raw as AwsCreds;
  }
  return {
    accessKeyId: raw.AccessKeyID ?? '',
    secretAccessKey: raw.SecretAccessKey ?? ''
  };
}

function toPortfolio(raw?: Portfolio | { RootEndpoint?: string; APIKey?: string }): Portfolio | undefined {
  if (!raw) return undefined;
  if ('rootEndpoint' in raw || 'apiKey' in raw) {
    return raw as Portfolio;
  }
  return {
    rootEndpoint: raw.RootEndpoint ?? '',
    apiKey: raw.APIKey ?? ''
  };
}

function toLLMProvider(raw?: LLMProvider | { Modal?: string; APIKey?: string }): LLMProvider | undefined {
  if (!raw) return undefined;
  if ('modal' in raw || 'apiKey' in raw) {
    return raw as LLMProvider;
  }
  return {
    modal: raw.Modal ?? '',
    apiKey: raw.APIKey ?? ''
  };
}

function toLLMConfig(raw?: LLMConfig | { Provider?: string; Providers?: Record<string, { Modal?: string; APIKey?: string }> }): LLMConfig | undefined {
  if (!raw) return undefined;
  if ('provider' in raw || 'providers' in raw) {
    return raw as LLMConfig;
  }
  const providers: Record<string, LLMProvider> = {};
  Object.entries(raw.Providers ?? {}).forEach(([key, value]) => {
    const provider = toLLMProvider(value);
    if (provider) {
      providers[key] = provider;
    }
  });
  return {
    provider: raw.Provider ?? 'ollama',
    providers
  };
}

export function normalizeUser(user: User): NormalizedUser {
  return {
    uuid: user.uuid,
    name: user.name,
    email: user.email,
    awsCreds: toAwsCreds(user.awsCreds ?? user.AwsCreds),
    portfolio: toPortfolio(user.portfolio ?? user.Portfolio),
    llmConfig: toLLMConfig(user.llmConfig ?? user.LLMConfig)
  };
}

export function normalizeInstanceResource(resource: InstanceResource): InstanceResource {
  return {
    id: resource.id ?? resource.ID,
    type: resource.type ?? resource.Type,
    name: resource.name ?? resource.Name,
    arn: resource.arn ?? resource.ARN,
    status: resource.status ?? resource.Status,
    region: resource.region ?? resource.Region,
    service: resource.service ?? resource.Service
  };
}

export function normalizeInstance(instance: InstanceRecord): NormalizedInstanceRecord {
  const resources = instance.resources ?? instance.Resources ?? [];
  return {
    uuid: instance.uuid ?? instance.UUID ?? '',
    name: instance.name ?? instance.Name ?? '',
    status: instance.status ?? instance.Status ?? '',
    resources: resources.map((res) => normalizeInstanceResource(res as InstanceResource)) as InstanceResource[]
  };
}
