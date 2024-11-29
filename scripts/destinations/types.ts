// Common types used across all destinations
interface Link {
  text: string;
  link: string;
}

interface Option {
  name: string;
  value: string;
  label?: string;
}

interface PreRequisites {
  featureFlags?: Array<{
    configKey: string;
    value?: boolean;
  }>;
  featureFlagsCondition?: 'and' | 'or';
  fields?: Array<{
    configKey: string;
    value: string;
  }>;
}

// Base field types
interface BaseField {
  type: string;
  label: string;
  value?: string;
  configKey?: string;
  required?: boolean;
  placeholder?: string;
  note?: string | Array<string | Link>;
  regex?: string;
  regexErrorMessage?: string;
  preRequisites?: PreRequisites;
  footerNote?: string;
  defaultValue?: string | boolean;
  options?: Option[];
  variant?: string;
  dynamicConfigSupported?: boolean;
}

// Specialized Field Types
interface TextInputField extends BaseField {
  type: 'textInput';
  secret?: boolean;
}

interface CopyField extends BaseField {
  type: 'copyField';
  copyText: string;
}

interface SelectField extends BaseField {
  type: 'select';
  options: Option[];
  defaultOption?: Option;
}

interface DynamicFormField extends BaseField {
  type: 'dynamicForm';
  labelLeft: string;
  labelRight: string;
  keyLeft: string;
  keyRight: string;
  placeholderLeft?: string;
  placeholderRight?: string;
  dynamicConfigSupported?: boolean;
}

interface DynamicCustomFormField extends BaseField {
  type: 'dynamicCustomForm';
  customFields: Record<string, any>[];
}

interface ToggleField extends BaseField {
  type: 'toggle';
}

interface CodeField extends BaseField {
  type: 'codeField';
  language: string;
}

interface InfoField extends BaseField {
  type: 'info';
  message: string;
}

// New Style Configuration Types
interface NewConfigSection {
  title: string;
  note?: string;
  icon?: string;
  fields: BaseField[];
  id?: string;
  groups?: {
    title: string;
    fields: BaseField[];
    note?: string | Array<string | Link>;
    icon?: string;
    callout?: {
      message: string;
      type: string;
    };
  }[];
}

interface NewConfigTemplate {
  title: string;
  note?: string;
  sections: NewConfigSection[];
  hideEditIcon?: boolean;
  fields: BaseField[];
}

interface Tab {
  name: string;
  fields: BaseField[];
}

interface RedirectGroup {
  tabs: Tab[];
}

interface NewStyleUIConfig {
  baseTemplate: NewConfigTemplate[];
  sdkTemplate?: NewConfigTemplate;
  redirectGroups?: Record<string, RedirectGroup>;
  consentSettingsTemplate?: NewConfigTemplate;
}

// Old Style Configuration Types
interface OldConfigSection {
  title: string;
  fields: BaseField[];
}

type OldStyleUIConfig = Array<OldConfigSection>;

// Destination Specific Types
interface BaseDestinationConfig {
  uiConfig: unknown;
}

interface NewStyleDestinationConfig extends BaseDestinationConfig {
  uiConfig: NewStyleUIConfig;
}

interface OldStyleDestinationConfig extends BaseDestinationConfig {
  uiConfig: OldStyleUIConfig;
}

// Union type for all possible field types
type Field =
  | TextInputField
  | CopyField
  | SelectField
  | DynamicFormField
  | DynamicCustomFormField
  | ToggleField
  | CodeField
  | InfoField;

// Union type for all destination configs
type DestinationConfig = NewStyleDestinationConfig | OldStyleDestinationConfig;

type UIConfig = { uiConfig: NewStyleUIConfig | OldStyleUIConfig };

// Type Guards
function isNewStyleConfig(uiConfig: NewStyleUIConfig): boolean {
  return uiConfig && 'baseTemplate' in uiConfig;
}

function isOldStyleConfig(uiConfig: OldStyleUIConfig): boolean {
  return Array.isArray(uiConfig);
}

// Destination-specific type helpers
type DestinationType =
  | 'adobe-analytics'
  | 'amplitude'
  | 'braze'
  | 'google-analytics-4'
  | 'heap'
  | 'hubspot'
  | 'intercom'
  | 'klaviyo'
  | 'mixpanel'
  | 'pinterest'
  | 'posthog'
  | 'rudderstack'
  | 'segment'
  | 'zapier';

interface DestinationTypeConfig {
  isNewStyle: boolean;
  hasSDKTemplate: boolean;
  hasConsentTemplate: boolean;
}

const destinationConfigs: Record<DestinationType, DestinationTypeConfig> = {
  'adobe-analytics': { isNewStyle: true, hasSDKTemplate: true, hasConsentTemplate: true },
  amplitude: { isNewStyle: true, hasSDKTemplate: true, hasConsentTemplate: true },
  braze: { isNewStyle: true, hasSDKTemplate: true, hasConsentTemplate: true },
  'google-analytics-4': { isNewStyle: true, hasSDKTemplate: true, hasConsentTemplate: true },
  heap: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  hubspot: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  intercom: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  klaviyo: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  mixpanel: { isNewStyle: true, hasSDKTemplate: true, hasConsentTemplate: true },
  pinterest: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  posthog: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  rudderstack: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  segment: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
  zapier: { isNewStyle: false, hasSDKTemplate: false, hasConsentTemplate: false },
};

export {
  Link,
  Option,
  PreRequisites,
  BaseField,
  Field,
  DynamicCustomFormField,
  NewStyleDestinationConfig,
  OldStyleDestinationConfig,
  DestinationConfig,
  DestinationType,
  OldStyleUIConfig,
  NewStyleUIConfig,
  destinationConfigs,
  UIConfig,
  isNewStyleConfig,
  isOldStyleConfig,
};
