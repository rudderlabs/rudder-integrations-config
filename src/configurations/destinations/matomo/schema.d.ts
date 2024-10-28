/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type MATOMO = {
  [k: string]: unknown;
} & {
  matomoVersion: "premise" | "cloud";
  siteId: string;
  useNativeSDK?: {
    web?: boolean;
    [k: string]: unknown;
  };
  eventsMapToGoalId?: {
    from?: string;
    to?: string;
    [k: string]: unknown;
  }[];
  eventsToStandard?: {
    from?: string;
    to?:
      | "ping"
      | "trackContentImpression"
      | "trackContentImpressionsWithinNode"
      | "trackContentInteraction"
      | "trackContentInteractionNode"
      | "trackLink"
      | "trackSiteSearch"
      | "";
    [k: string]: unknown;
  }[];
  trackAllContentImpressions?: boolean;
  trackVisibleContentImpressions?: boolean;
  logAllContentBlocksOnPage?: boolean;
  enableHeartBeatTimer?: boolean;
  enableLinkTracking?: boolean;
  disablePerformanceTracking?: boolean;
  enableCrossDomainLinking?: boolean;
  setCrossDomainLinkingTimeout?: boolean;
  getCrossDomainLinkingUrlParameter?: boolean;
  disableBrowserFeatureDetection?: boolean;
  oneTrustCookieCategories?: {
    web?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    web?: "device";
    [k: string]: unknown;
  };
  consentManagement?: {
    web?: {
      [k: string]: unknown;
    }[];
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
};