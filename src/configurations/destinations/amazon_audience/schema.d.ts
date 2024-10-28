/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface AMAZON_AUDIENCE {
  authServer: "North America";
  advertiserId?: string;
  externalAudienceId?: string;
  ttl?: string;
  enableHash?: boolean;
  dataSourceCountry?: {
    country?: string;
    [k: string]: unknown;
  }[];
  oneTrustCookieCategories?: {
    warehouse?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  consentManagement?: {
    warehouse?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  ketchConsentPurposes?: {
    warehouse?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    cloud?: "cloud";
    warehouse?: "cloud";
    [k: string]: unknown;
  };
  [k: string]: unknown;
}
