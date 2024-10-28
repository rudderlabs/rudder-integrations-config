/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type KAFKA = {
  [k: string]: unknown;
} & {
  hostName: string;
  port: string;
  topic: string;
  sslEnabled?: boolean;
  caCertificate?: string;
  useSSH?: boolean;
  sshHost?: string;
  sshPort?: string;
  sshUser?: string;
  sshPublicKey?: string;
  useSASL?: boolean;
  saslType?: "plain" | "sha256" | "sha512";
  username?: string;
  password?: string;
  convertToAvro?: boolean;
  avroSchemas?: {
    schemaId?: string;
    schema?: string;
    [k: string]: unknown;
  }[];
  embedAvroSchemaID?: boolean;
  connectionMode?: {
    web?: "cloud";
    android?: "cloud";
    ios?: "cloud";
    unity?: "cloud";
    amp?: "cloud";
    cloud?: "cloud";
    warehouse?: "cloud";
    reactnative?: "cloud";
    flutter?: "cloud";
    cordova?: "cloud";
    shopify?: "cloud";
    [k: string]: unknown;
  };
  consentManagement?: {
    cloud?: {
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
    warehouse?: {
      [k: string]: unknown;
    }[];
    [k: string]: unknown;
  };
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
};
