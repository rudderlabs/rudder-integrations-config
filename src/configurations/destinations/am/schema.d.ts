/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface AM {
  apiKey: string;
  residencyServer: "standard" | "EU";
  proxyServerUrl?: {
    web?: string;
    [k: string]: unknown;
  };
  trackAllPages?: boolean;
  trackCategorizedPages?: boolean;
  trackNamedPages?: boolean;
  useUserDefinedPageEventName?: boolean;
  userProvidedPageEventString?: string;
  groupTypeTrait?: string;
  groupValueTrait?: string;
  traitsToIncrement?: {
    traits?: string;
    [k: string]: unknown;
  }[];
  traitsToSetOnce?: {
    traits?: string;
    [k: string]: unknown;
  }[];
  traitsToAppend?: {
    traits?: string;
    [k: string]: unknown;
  }[];
  traitsToPrepend?: {
    traits?: string;
    [k: string]: unknown;
  }[];
  enableEnhancedUserOperations?: boolean;
  apiSecret?: string;
  versionName?: string;
  mapDeviceBrand?: boolean;
  trackProductsOnce?: boolean;
  trackRevenuePerProduct?: boolean;
  useUserDefinedScreenEventName?: boolean;
  userProvidedScreenEventString?: string;
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
    web?: {
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
  enableLocationListening?: {
    android?: boolean;
    reactnative?: boolean;
    flutter?: boolean;
    [k: string]: unknown;
  };
  trackSessionEvents?: {
    android?: boolean;
    ios?: boolean;
    reactnative?: boolean;
    flutter?: boolean;
    [k: string]: unknown;
  };
  useAdvertisingIdForDeviceId?: {
    android?: boolean;
    reactnative?: boolean;
    flutter?: boolean;
    [k: string]: unknown;
  };
  useIdfaAsDeviceId?: {
    ios?: boolean;
    reactnative?: boolean;
    flutter?: boolean;
    [k: string]: unknown;
  };
  attribution?: {
    web?: boolean;
    [k: string]: unknown;
  };
  trackUtmProperties?: {
    web?: boolean;
    [k: string]: unknown;
  };
  trackNewCampaigns?: {
    web?: boolean;
    [k: string]: unknown;
  };
  unsetParamsReferrerOnNewSession?: {
    web?: boolean;
    [k: string]: unknown;
  };
  batchEvents?: {
    web?: boolean;
    [k: string]: unknown;
  };
  eventUploadPeriodMillis?: {
    android?: string;
    ios?: string;
    web?: string;
    reactnative?: string;
    flutter?: string;
    [k: string]: unknown;
  };
  eventUploadThreshold?: {
    android?: string;
    ios?: string;
    web?: string;
    reactnative?: string;
    flutter?: string;
    [k: string]: unknown;
  };
  useNativeSDK?: {
    android?: boolean;
    ios?: boolean;
    web?: boolean;
    reactnative?: boolean;
    flutter?: boolean;
    [k: string]: unknown;
  };
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
    web?: {
      [k: string]: unknown;
    }[];
    unity?: {
      [k: string]: unknown;
    }[];
    amp?: {
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
  connectionMode?: {
    web?: "cloud" | "device";
    android?: "cloud" | "device";
    ios?: "cloud" | "device";
    flutter?: "cloud" | "device";
    reactnative?: "cloud" | "device";
    unity?: "cloud";
    amp?: "cloud";
    cordova?: "cloud";
    shopify?: "cloud";
    cloud?: "cloud";
    warehouse?: "cloud";
    [k: string]: unknown;
  };
  preferAnonymousIdForDeviceId?: {
    web?: boolean;
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
    web?: {
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