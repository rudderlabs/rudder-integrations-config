/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type YAHOO_DSP = {
  [k: string]: unknown;
} & {
  clientId: string;
  clientSecret: string;
  accountId: string;
  audienceType: "EMAIL" | "DEVICE_ID" | "IP_ADDRESS";
  audienceId: string;
  hashRequired?: boolean;
  oneTrustCookieCategories?: {
    cloud?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    warehouse?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    shopify?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  consentManagement?: {
    cloud?: {
      [k: string]: unknown;
    }[];
    warehouse?: {
      [k: string]: unknown;
    }[];
    shopify?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    shopify?: "cloud";
    cloud?: "cloud";
    warehouse?: "cloud";
    [k: string]: unknown;
  };
  ketchConsentPurposes?: {
    cloud?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    warehouse?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    shopify?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  [k: string]: unknown;
};
