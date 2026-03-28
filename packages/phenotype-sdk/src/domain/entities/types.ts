/**
 * Feature flag types and enums.
 */

export type Stage = 'SP' | 'AP' | 'GA' | 'GA+';

export type TransienceClass = 'P' | 'F' | 'T';

export type FlagState = 'disabled' | 'enabled';

export const StageDescriptions: Record<Stage, string> = {
  'SP': 'Soft Preview - Early access for testing',
  'AP': 'Advanced Preview - Broader testing',
  'GA': 'General Availability - Full release',
  'GA+': 'General Availability Plus - Stable mature release',
};

export const TransienceClassDescriptions: Record<TransienceClass, string> = {
  'P': 'Permanent - Intended to stay indefinitely',
  'F': 'Feature - Beta/experimental feature',
  'T': 'Temporary - Will be removed',
};
