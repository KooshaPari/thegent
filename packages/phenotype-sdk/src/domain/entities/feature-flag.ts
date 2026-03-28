/**
 * Feature flag entity.
 */

import { FlagState, Stage, TransienceClass } from './types.js';

/**
 * Feature flag for controlling feature rollouts.
 */
export class FeatureFlag {
  public readonly id: string;
  public name: string;
  public enabled: boolean;
  public readonly namespace: string;
  public description: string;
  public stage: Stage;
  public transienceClass: TransienceClass;
  public channels: string[];
  public retireAtStage?: Stage;
  public readonly createdAt: Date;
  public updatedAt: Date;

  private constructor(params: {
    id: string;
    name: string;
    enabled: boolean;
    namespace: string;
    description: string;
    stage: Stage;
    transienceClass: TransienceClass;
    channels: string[];
    retireAtStage?: Stage;
    createdAt: Date;
    updatedAt: Date;
  }) {
    this.id = params.id;
    this.name = params.name;
    this.enabled = params.enabled;
    this.namespace = params.namespace;
    this.description = params.description;
    this.stage = params.stage;
    this.transienceClass = params.transienceClass;
    this.channels = params.channels;
    this.retireAtStage = params.retireAtStage;
    this.createdAt = params.createdAt;
    this.updatedAt = params.updatedAt;
  }

  static create(params: {
    name: string;
    namespace?: string;
    description?: string;
    channels?: string[];
  }): FeatureFlag {
    const now = new Date();
    return new FeatureFlag({
      id: generateFlagId(),
      name: params.name,
      enabled: false,
      namespace: params.namespace ?? 'default',
      description: params.description ?? '',
      stage: 'SP', // Soft Preview
      transienceClass: 'F', // Permanent
      channels: params.channels ?? ['dev'],
      createdAt: now,
      updatedAt: now,
    });
  }

  enable(): void {
    this.enabled = true;
    this.updatedAt = new Date();
  }

  disable(): void {
    this.enabled = false;
    this.updatedAt = new Date();
  }

  promote(): void {
    const stages: Stage[] = ['SP', 'AP', 'GA', 'GA+'];
    const currentIndex = stages.indexOf(this.stage);
    if (currentIndex < stages.length - 1) {
      this.stage = stages[currentIndex + 1];
      this.updatedAt = new Date();
    }
  }

  isActiveForChannel(channel: string): boolean {
    return this.channels.includes(channel);
  }

  shouldRetire(): boolean {
    return this.retireAtStage !== undefined &&
           stagesOrder(this.stage) >= stagesOrder(this.retireAtStage);
  }

  toJSON(): FeatureFlagJSON {
    return {
      id: this.id,
      name: this.name,
      enabled: this.enabled,
      namespace: this.namespace,
      description: this.description,
      stage: this.stage,
      transience_class: this.transienceClass,
      channels: this.channels,
      retire_at_stage: this.retireAtStage,
      created_at: this.createdAt.toISOString(),
      updated_at: this.updatedAt.toISOString(),
    };
  }
}

export interface FeatureFlagJSON {
  id: string;
  name: string;
  enabled: boolean;
  namespace: string;
  description: string;
  stage: Stage;
  transience_class: TransienceClass;
  channels: string[];
  retire_at_stage?: Stage;
  created_at: string;
  updated_at: string;
}

function generateFlagId(): string {
  return `flag_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
}

const stageOrder: Record<Stage, number> = {
  'SP': 0,  // Soft Preview
  'AP': 1,  // Advanced Preview
  'GA': 2,  // General Availability
  'GA+': 3, // General Availability Plus
};

function stagesOrder(stage: Stage): number {
  return stageOrder[stage] ?? 0;
}

export * from './types.js';
