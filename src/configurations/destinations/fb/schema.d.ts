/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface FB {
  consentManagement?: {
    cloud?: {
      [k: string]: unknown;
    }[];
    warehouse?: {
      [k: string]: unknown;
    }[];
    android?: {
      [k: string]: unknown;
    }[];
    ios?: {
      [k: string]: unknown;
    }[];
    unity?: {
      [k: string]: unknown;
    }[];
    reactnative?: {
      [k: string]: unknown;
    }[];
    flutter?: {
      [k: string]: unknown;
    }[];
    cordova?: {
      [k: string]: unknown;
    }[];
    shopify?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  appID: string;
  limitedDataUse?: boolean;
  dpoState?: "0" | "1000";
  dpoCountry?: "0" | "1";
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
    unity?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    amp?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    cloud?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    warehouse?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    reactnative?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    flutter?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    cordova?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    shopify?: {
      oneTrustCookieCategory?: string;
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
  connectionMode?: {
    android?: "cloud" | "device";
    ios?: "cloud" | "device";
    web?: "cloud";
    unity?: "cloud";
    amp?: "cloud";
    reactnative?: "cloud" | "device";
    flutter?: "cloud";
    cordova?: "cloud";
    shopify?: "cloud";
    cloud?: "cloud";
    warehouse?: "cloud";
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
    unity?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    amp?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    cloud?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    warehouse?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    reactnative?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    flutter?: {
      purpose?: string;
      [k: string]: unknown;
    }[];
    cordova?: {
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
}
