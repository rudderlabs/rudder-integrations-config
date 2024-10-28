/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface COMSCORE {
  publisherId: string;
  appName?: string;
  foregroundOnly?: boolean;
  foregroundAndBackground?: boolean;
  autoUpdateInterval?: string;
  useNativeSDK?: {
    android?: boolean;
    ios?: boolean;
    [k: string]: unknown;
  };
  eventFilteringOption?: "disable" | "whitelistedEvents" | "blacklistedEvents";
  whitelistedEvents?: {
    eventName?: string;
    [k: string]: unknown;
  }[];
  blacklistedEvents?: {
    eventName?: string;
    [k: string]: unknown;
  }[];
  oneTrustCookieCategories?: {
    android?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    ios?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  consentManagement?: {
    android?: {
      [k: string]: unknown;
    }[];
    ios?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    android?: "device";
    ios?: "device";
    [k: string]: unknown;
  };
  ketchConsentPurposes?: {
    android?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    ios?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  [k: string]: unknown;
}