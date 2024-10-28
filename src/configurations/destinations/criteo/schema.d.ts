/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface CRITEO {
  accountId: string;
  homePageUrl?: string;
  hashMethod?: "none" | "md5" | "sha256" | "both";
  fieldMapping?: {
    from?: string;
    to?: string;
    [k: string]: unknown;
  }[];
  useNativeSDK?: {
    web?: boolean;
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
    web?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  eventsToStandard?: {
    from?: string;
    to?: "product viewed" | "cart viewed" | "order completed" | "product list viewed" | "product added" | "";
    [k: string]: unknown;
  }[];
  consentManagement?: {
    web?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    web?: "device";
    [k: string]: unknown;
  };
  ketchConsentPurposes?: {
    web?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  [k: string]: unknown;
}
