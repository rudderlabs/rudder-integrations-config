import fs from 'fs';
import path from 'path';
import glob from 'glob';
import {
  init,
  validateConfig,
  validateDestinationDefinitions,
  validateSourceDefinitions,
  validateAccountDefinitions,
} from '../../src/validator';

// Also import from main entry point to test exports
import * as mainExports from '../../src';

// Mock file system and glob
jest.mock('fs');
jest.mock('glob');
jest.mock('path');

const mockedFs = fs as jest.Mocked<typeof fs>;
const mockedGlob = glob as jest.MockedFunction<typeof glob>;
const mockedPath = path as jest.Mocked<typeof path>;

describe('Validator Utils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset validators cache
    jest.resetModules();
  });

  describe('Module exports', () => {
    it('should export all validator functions from main entry point', () => {
      expect(mainExports.init).toBeDefined();
      expect(mainExports.validateConfig).toBeDefined();
      expect(mainExports.validateDestinationDefinitions).toBeDefined();
      expect(mainExports.validateSourceDefinitions).toBeDefined();
      expect(mainExports.validateAccountDefinitions).toBeDefined();

      // Verify they are functions
      expect(typeof mainExports.init).toBe('function');
      expect(typeof mainExports.validateConfig).toBe('function');
      expect(typeof mainExports.validateDestinationDefinitions).toBe('function');
      expect(typeof mainExports.validateSourceDefinitions).toBe('function');
      expect(typeof mainExports.validateAccountDefinitions).toBe('function');
    });
  });

  describe('init()', () => {
    it('should initialize validators successfully', async () => {
      const mockSchemaFiles = [
        '/path/to/destinations/ga/schema.json',
        '/path/to/sources/shopify/schema.json',
      ];

      const mockSchemaContent1 = {
        configSchema: {
          type: 'object',
          properties: {
            apiKey: { type: 'string' },
          },
          required: ['apiKey'],
        },
      };

      const mockSchemaContent2 = {
        configSchema: {
          type: 'object',
          properties: {
            shopUrl: { type: 'string' },
          },
          required: ['shopUrl'],
        },
      };

      // Mock glob to return schema files
      mockedGlob.mockResolvedValue(mockSchemaFiles);

      // Mock path operations
      mockedPath.dirname
        .mockReturnValueOnce('/path/to/destinations/ga')
        .mockReturnValueOnce('/path/to/sources/shopify');
      mockedPath.basename
        .mockReturnValueOnce('ga')
        .mockReturnValueOnce('destinations')
        .mockReturnValueOnce('shopify')
        .mockReturnValueOnce('sources');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      // Mock fs.promises.readFile
      mockedFs.promises = {
        readFile: jest
          .fn()
          .mockResolvedValueOnce(JSON.stringify(mockSchemaContent1))
          .mockResolvedValueOnce(JSON.stringify(mockSchemaContent2)),
      } as any;

      await init();

      expect(mockedGlob).toHaveBeenCalledWith('/path/to/configurations/**/schema.json');
      expect(mockedFs.promises.readFile).toHaveBeenCalledTimes(2);
    });

    it('should handle empty schema files', async () => {
      mockedGlob.mockResolvedValue([]);
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      await expect(init()).resolves.not.toThrow();
      expect(mockedGlob).toHaveBeenCalledWith('/path/to/configurations/**/schema.json');
    });

    it('should handle schema files with no configSchema property', async () => {
      const mockSchemaFiles = ['/path/to/destinations/ga/schema.json'];

      const mockSchemaContent = {
        // No configSchema property - should use empty object as fallback
        someOtherProperty: 'value',
      };

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.dirname.mockReturnValue('/path/to/destinations/ga');
      mockedPath.basename.mockReturnValueOnce('ga').mockReturnValueOnce('destinations');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(mockSchemaContent)),
      } as any;

      await expect(init()).resolves.not.toThrow();
    });

    it('should handle schema files with null configSchema', async () => {
      const mockSchemaFiles = ['/path/to/destinations/ga/schema.json'];

      const mockSchemaContent = {
        configSchema: null,
      };

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.dirname.mockReturnValue('/path/to/destinations/ga');
      mockedPath.basename.mockReturnValueOnce('ga').mockReturnValueOnce('destinations');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(mockSchemaContent)),
      } as any;

      await expect(init()).resolves.not.toThrow();
    });

    it('should handle invalid JSON in schema files', async () => {
      const mockSchemaFiles = ['/path/to/destinations/ga/schema.json'];

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');
      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue('invalid json'),
      } as any;

      await expect(init()).rejects.toThrow();
    });

    it('should handle file read errors', async () => {
      const mockSchemaFiles = ['/path/to/destinations/ga/schema.json'];

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');
      mockedFs.promises = {
        readFile: jest.fn().mockRejectedValue(new Error('File read error')),
      } as any;

      await expect(init()).rejects.toThrow('File read error');
    });
  });

  describe('validateConfig()', () => {
    beforeEach(async () => {
      // Setup basic validators for testing
      const mockSchemaFiles = [
        '/path/to/destinations/ga/schema.json',
        '/path/to/destinations/facebook/schema.json',
      ];

      const validSchema = {
        configSchema: {
          type: 'object',
          properties: {
            apiKey: { type: 'string' },
            enabled: { type: 'boolean' },
          },
          required: ['apiKey'],
        },
      };

      const invalidSchema = {
        configSchema: {
          type: 'object',
          properties: {
            requiredField: { type: 'string' },
          },
          required: ['requiredField'],
        },
      };

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.dirname
        .mockReturnValueOnce('/path/to/destinations/ga')
        .mockReturnValueOnce('/path/to/destinations/facebook');
      mockedPath.basename
        .mockReturnValueOnce('ga')
        .mockReturnValueOnce('destinations')
        .mockReturnValueOnce('facebook')
        .mockReturnValueOnce('destinations');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      mockedFs.promises = {
        readFile: jest
          .fn()
          .mockResolvedValueOnce(JSON.stringify(validSchema))
          .mockResolvedValueOnce(JSON.stringify(invalidSchema)),
      } as any;

      await init();
    });

    it('should throw error for missing definitionName', () => {
      expect(() => {
        validateConfig('', {}, 'destinations');
      }).toThrow('Missing definitionName');
    });

    it('should throw error for null definitionName', () => {
      expect(() => {
        validateConfig(null as any, {}, 'destinations');
      }).toThrow('Missing definitionName');
    });

    it('should throw error for undefined definitionName', () => {
      expect(() => {
        validateConfig(undefined as any, {}, 'destinations');
      }).toThrow('Missing definitionName');
    });

    it('should throw error for unknown integration when throwErrorOnMissingValidations is true', () => {
      expect(() => {
        validateConfig('unknown_integration', {}, 'destinations', true);
      }).toThrow('No validation method found for definition unknown_integration');
    });

    it('should not throw error for unknown integration when throwErrorOnMissingValidations is false', () => {
      expect(() => {
        validateConfig('unknown_integration', {}, 'destinations', false);
      }).not.toThrow();
    });

    it('should not throw error for unknown integration when throwErrorOnMissingValidations is undefined', () => {
      expect(() => {
        validateConfig('unknown_integration', {}, 'destinations');
      }).not.toThrow();
    });

    it('should validate valid configuration successfully', () => {
      const validConfig = {
        apiKey: 'test-api-key',
        enabled: true,
      };

      expect(() => {
        validateConfig('ga', validConfig, 'destinations');
      }).not.toThrow();
    });

    it('should throw error for invalid configuration', () => {
      const invalidConfig = {
        enabled: true,
        // missing required apiKey
      };

      expect(() => {
        validateConfig('ga', invalidConfig, 'destinations');
      }).toThrow();
    });

    it('should provide meaningful error messages for validation failures', () => {
      const invalidConfig = {};

      expect(() => {
        validateConfig('facebook', invalidConfig, 'destinations');
      }).toThrow(/requiredField/);
    });

    it('should handle configuration with extra properties', () => {
      const configWithExtra = {
        apiKey: 'test-api-key',
        enabled: true,
        extraProperty: 'should not cause error',
      };

      expect(() => {
        validateConfig('ga', configWithExtra, 'destinations');
      }).not.toThrow();
    });

    it('should handle different integration types', () => {
      const validConfig = {
        apiKey: 'test-api-key',
      };

      expect(() => {
        validateConfig('ga', validConfig, 'sources');
      }).not.toThrow();
    });

    it('should handle validation when validator exists but validation passes', () => {
      const validConfig = {
        apiKey: 'test-api-key',
      };

      const result = validateConfig('ga', validConfig, 'destinations');
      expect(result).toBeUndefined();
    });
  });

  describe('validateDestinationDefinitions()', () => {
    beforeEach(() => {
      mockedPath.join.mockReturnValue('/path/to/schemas/destinations/db-config-schema.json');

      const validDestinationSchema = {
        type: 'object',
        required: ['name', 'displayName', 'config'],
        properties: {
          name: {
            type: 'string',
            pattern: '^[a-zA-Z0-9_-]+$',
          },
          displayName: {
            type: 'string',
            pattern: '^[a-zA-Z0-9_ .\\-\\(\\)/]+$',
          },
          config: {
            type: 'object',
            required: ['supportedSourceTypes', 'destConfig'],
            properties: {
              supportedSourceTypes: {
                type: 'array',
                items: { type: 'string' },
                minItems: 1,
              },
              destConfig: {
                type: 'object',
                minProperties: 1,
              },
            },
          },
        },
      };

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(validDestinationSchema)),
      } as any;
    });

    it('should validate valid destination definition', async () => {
      const validDestDef = {
        name: 'GOOGLE_ANALYTICS',
        displayName: 'Google Analytics',
        config: {
          supportedSourceTypes: ['web', 'android', 'ios'],
          destConfig: {
            defaultConfig: ['apiKey', 'trackingId'],
          },
        },
      };

      await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
    });

    it('should throw error for invalid destination definition', async () => {
      const invalidDestDef = {
        name: 'GOOGLE_ANALYTICS',
        // missing required displayName and config
      };

      await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow();
    });

    it('should throw error for destination definition with invalid name pattern', async () => {
      const invalidDestDef = {
        name: 'GOOGLE ANALYTICS!', // invalid pattern
        displayName: 'Google Analytics',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['apiKey'],
          },
        },
      };

      await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow();
    });

    it('should throw error for destination definition with empty supportedSourceTypes', async () => {
      const invalidDestDef = {
        name: 'GOOGLE_ANALYTICS',
        displayName: 'Google Analytics',
        config: {
          supportedSourceTypes: [], // should have minItems: 1
          destConfig: {
            defaultConfig: ['apiKey'],
          },
        },
      };

      await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow();
    });

    it('should handle schema loading errors', async () => {
      mockedFs.promises = {
        readFile: jest.fn().mockRejectedValue(new Error('File not found')),
      } as any;

      const validDestDef = {
        name: 'GOOGLE_ANALYTICS',
        displayName: 'Google Analytics',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['apiKey'],
          },
        },
      };

      await expect(validateDestinationDefinitions(validDestDef)).rejects.toThrow('File not found');
    });

    it('should handle validation when errors array is empty', async () => {
      // This test ensures we cover the case where validator.errors might be empty
      const validDestDef = {
        name: 'GOOGLE_ANALYTICS',
        displayName: 'Google Analytics',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['apiKey'],
          },
        },
      };

      const result = await validateDestinationDefinitions(validDestDef);
      expect(result).toBe(true);
    });
  });

  describe('validateSourceDefinitions()', () => {
    beforeEach(() => {
      mockedPath.join.mockReturnValue('/path/to/schemas/sources/db-config-schema.json');

      const validSourceSchema = {
        type: 'object',
        required: ['name', 'displayName', 'type'],
        properties: {
          name: {
            type: 'string',
            pattern: '^[a-zA-Z0-9_-]+$',
          },
          displayName: {
            type: 'string',
            pattern: '^[a-zA-Z0-9_ .\\-\\(\\)/]+$',
          },
          type: {
            type: 'string',
            enum: ['cloud', 'web', 'android', 'androidKotlin', 'ios', 'iosSwift'],
          },
        },
      };

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(validSourceSchema)),
      } as any;
    });

    it('should validate valid source definition', async () => {
      const validSourceDef = {
        name: 'shopify',
        displayName: 'Shopify',
        type: 'cloud',
      };

      await expect(validateSourceDefinitions(validSourceDef)).resolves.toBe(true);
    });

    it('should throw error for invalid source definition', async () => {
      const invalidSourceDef = {
        name: 'shopify',
        // missing required displayName and type
      };

      await expect(validateSourceDefinitions(invalidSourceDef)).rejects.toThrow();
    });

    it('should throw error for source definition with invalid type', async () => {
      const invalidSourceDef = {
        name: 'shopify',
        displayName: 'Shopify',
        type: 'invalid_type', // not in enum
      };

      await expect(validateSourceDefinitions(invalidSourceDef)).rejects.toThrow();
    });

    it('should handle schema loading errors', async () => {
      mockedFs.promises = {
        readFile: jest.fn().mockRejectedValue(new Error('Schema file not found')),
      } as any;

      const validSourceDef = {
        name: 'shopify',
        displayName: 'Shopify',
        type: 'cloud',
      };

      await expect(validateSourceDefinitions(validSourceDef)).rejects.toThrow(
        'Schema file not found',
      );
    });

    it('should handle validation when errors array is empty', async () => {
      const validSourceDef = {
        name: 'shopify',
        displayName: 'Shopify',
        type: 'cloud',
      };

      const result = await validateSourceDefinitions(validSourceDef);
      expect(result).toBe(true);
    });
  });

  describe('validateAccountDefinitions()', () => {
    beforeEach(() => {
      mockedPath.join.mockReturnValue('/path/to/schemas/account/account-db-config-schema.json');

      const validAccountSchema = {
        type: 'object',
        required: ['name', 'type', 'category', 'authenticationType', 'config'],
        properties: {
          name: {
            type: 'string',
            pattern: '^[A-Z_]+$',
          },
          type: {
            type: 'string',
          },
          category: {
            type: 'string',
            enum: ['destination', 'source'],
          },
          authenticationType: {
            type: 'string',
          },
          config: {
            type: 'object',
            properties: {
              optionFields: {
                type: 'array',
                items: { type: 'string' },
              },
              refreshOAuthToken: {
                type: 'boolean',
              },
            },
            additionalProperties: false,
          },
        },
        additionalProperties: false,
      };

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(validAccountSchema)),
      } as any;
    });

    it('should validate valid account definition', async () => {
      const validAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'destination',
        authenticationType: 'OAuth2',
        config: {
          optionFields: ['clientId', 'clientSecret'],
          refreshOAuthToken: true,
        },
      };

      await expect(validateAccountDefinitions(validAccountDef)).resolves.toBe(true);
    });

    it('should throw error for invalid account definition', async () => {
      const invalidAccountDef = {
        name: 'GOOGLE_ADS',
        // missing required fields
      };

      await expect(validateAccountDefinitions(invalidAccountDef)).rejects.toThrow();
    });

    it('should throw error for account definition with invalid name pattern', async () => {
      const invalidAccountDef = {
        name: 'google_ads', // should be uppercase
        type: 'OAuth',
        category: 'destination',
        authenticationType: 'OAuth2',
        config: {},
      };

      await expect(validateAccountDefinitions(invalidAccountDef)).rejects.toThrow();
    });

    it('should throw error for account definition with invalid category', async () => {
      const invalidAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'invalid_category', // not in enum
        authenticationType: 'OAuth2',
        config: {},
      };

      await expect(validateAccountDefinitions(invalidAccountDef)).rejects.toThrow();
    });

    it('should throw error for account definition with extra properties', async () => {
      const invalidAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'destination',
        authenticationType: 'OAuth2',
        config: {},
        extraProperty: 'not allowed', // additionalProperties: false
      };

      await expect(validateAccountDefinitions(invalidAccountDef)).rejects.toThrow();
    });

    it('should validate account definition with minimal config', async () => {
      const validAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'source',
        authenticationType: 'OAuth2',
        config: {},
      };

      await expect(validateAccountDefinitions(validAccountDef)).resolves.toBe(true);
    });

    it('should handle schema loading errors', async () => {
      mockedFs.promises = {
        readFile: jest.fn().mockRejectedValue(new Error('Account schema not found')),
      } as any;

      const validAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'destination',
        authenticationType: 'OAuth2',
        config: {},
      };

      await expect(validateAccountDefinitions(validAccountDef)).rejects.toThrow(
        'Account schema not found',
      );
    });

    it('should handle validation when errors array is empty', async () => {
      const validAccountDef = {
        name: 'GOOGLE_ADS',
        type: 'OAuth',
        category: 'destination',
        authenticationType: 'OAuth2',
        config: {},
      };

      const result = await validateAccountDefinitions(validAccountDef);
      expect(result).toBe(true);
    });
  });

  describe('Error message formatting', () => {
    beforeEach(async () => {
      const mockSchemaFiles = ['/path/to/destinations/test/schema.json'];

      const complexSchema = {
        configSchema: {
          type: 'object',
          properties: {
            user: {
              type: 'object',
              properties: {
                profile: {
                  type: 'object',
                  properties: {
                    name: { type: 'string' },
                    age: { type: 'number', minimum: 0 },
                  },
                  required: ['name'],
                },
              },
              required: ['profile'],
            },
          },
          required: ['user'],
        },
      };

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.dirname.mockReturnValue('/path/to/destinations/test');
      mockedPath.basename.mockReturnValueOnce('test').mockReturnValueOnce('destinations');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(complexSchema)),
      } as any;

      await init();
    });

    it('should format nested property errors correctly', () => {
      const invalidConfig = {
        user: {
          profile: {
            age: -5, // invalid: minimum 0
            // missing required name
          },
        },
      };

      expect(() => {
        validateConfig('test', invalidConfig, 'destinations');
      }).toThrow();
    });

    it('should format missing required field errors correctly', () => {
      const invalidConfig = {
        // missing required user
      };

      let errorMessage = '';
      try {
        validateConfig('test', invalidConfig, 'destinations');
      } catch (error) {
        errorMessage = error.message;
      }

      expect(errorMessage).toContain('must have required property');
    });

    it('should handle error message formatting with deep nested paths', () => {
      const invalidConfig = {
        user: {
          profile: {
            name: 'John',
            age: -5, // This should trigger a minimum validation error
          },
        },
      };

      let errorMessage = '';
      try {
        validateConfig('test', invalidConfig, 'destinations');
      } catch (error) {
        errorMessage = error.message;
      }

      expect(errorMessage).toContain('user.profile.age');
    });
  });

  describe('Integration with real validator module', () => {
    // Test actual module behavior without mocks for critical paths
    beforeAll(() => {
      jest.unmock('fs');
      jest.unmock('glob');
      jest.unmock('path');
    });

    afterAll(() => {
      jest.mock('fs');
      jest.mock('glob');
      jest.mock('path');
    });

    it('should handle empty definition name correctly', () => {
      expect(() => {
        validateConfig('', {}, 'destinations');
      }).toThrow('Missing definitionName');
    });

    it('should handle null/undefined config correctly', () => {
      expect(() => {
        validateConfig('', null as any, 'destinations');
      }).toThrow('Missing definitionName');

      expect(() => {
        validateConfig('', undefined as any, 'destinations');
      }).toThrow('Missing definitionName');
    });
  });

  describe('Edge cases and error handling', () => {
    beforeEach(async () => {
      // Setup a validator with strict validation for edge case testing
      const mockSchemaFiles = ['/path/to/destinations/strict/schema.json'];

      const strictSchema = {
        configSchema: {
          type: 'object',
          properties: {
            apiKey: {
              type: 'string',
              minLength: 10,
            },
            timeout: {
              type: 'number',
              minimum: 100,
              maximum: 5000,
            },
          },
          required: ['apiKey'],
          additionalProperties: false,
        },
      };

      mockedGlob.mockResolvedValue(mockSchemaFiles);
      mockedPath.dirname.mockReturnValue('/path/to/destinations/strict');
      mockedPath.basename.mockReturnValueOnce('strict').mockReturnValueOnce('destinations');
      mockedPath.join.mockReturnValue('/path/to/configurations/**/schema.json');

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(strictSchema)),
      } as any;

      await init();
    });

    it('should handle multiple validation errors in single config', () => {
      const invalidConfig = {
        apiKey: 'short', // too short
        timeout: 10000, // too large
        extraProp: 'not allowed',
      };

      expect(() => {
        validateConfig('strict', invalidConfig, 'destinations');
      }).toThrow();
    });

    it('should handle config with wrong data types', () => {
      const invalidConfig = {
        apiKey: 123, // should be string
        timeout: 'not a number', // should be number
      };

      expect(() => {
        validateConfig('strict', invalidConfig, 'destinations');
      }).toThrow();
    });

    it('should handle empty object configuration', () => {
      const emptyConfig = {};

      expect(() => {
        validateConfig('strict', emptyConfig, 'destinations');
      }).toThrow();
    });
  });

  describe('Custom Validation Rules for Destination Definitions', () => {
    beforeEach(() => {
      mockedPath.join.mockReturnValue('/path/to/schemas/destinations/db-config-schema.json');

      const minimalDestinationSchema = {
        type: 'object',
        required: ['name', 'displayName', 'config'],
        properties: {
          name: { type: 'string' },
          displayName: { type: 'string' },
          config: { type: 'object' },
        },
      };

      mockedFs.promises = {
        readFile: jest.fn().mockResolvedValue(JSON.stringify(minimalDestinationSchema)),
      } as any;
    });

    describe('Rule: secretKeys-not-in-includeKeys', () => {
      it('should pass when no secrets are in includeKeys', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['password', 'apiSecret'],
            includeKeys: ['apiKey', 'enabled'],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should fail when a secret is in includeKeys but not in excludeKeys', async () => {
        const invalidDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['apiKey', 'password'],
            includeKeys: ['apiKey', 'enabled'],
          },
        };

        await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow(
          /Secret keys must not be exposed to client-side.*apiKey/,
        );
      });

      it('should pass when secret is in both includeKeys and excludeKeys (excludeKeys wins)', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['apiKey', 'password'],
            includeKeys: ['apiKey', 'enabled'],
            excludeKeys: ['apiKey', 'password'],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should fail when multiple secrets are in includeKeys but not in excludeKeys', async () => {
        const invalidDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['apiKey', 'password', 'token'],
            includeKeys: ['apiKey', 'password', 'enabled'],
          },
        };

        await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow(
          /Secret keys must not be exposed to client-side/,
        );
      });

      it('should pass when includeKeys is empty', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['apiKey', 'password'],
            includeKeys: [],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when includeKeys is undefined', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: ['apiKey', 'password'],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when secretKeys is empty', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            secretKeys: [],
            includeKeys: ['apiKey', 'enabled'],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when secretKeys is undefined', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: ['apiKey', 'enabled'],
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });
    });

    describe('Rule: includeKeys-must-be-defined-when-device-hybrid-mode-is-supported', () => {
      it('should pass when includeKeys is defined and device mode is supported', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: ['apiKey'],
            supportedConnectionModes: {
              web: ['device'],
            },
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when includeKeys is defined and hybrid mode is supported', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: ['apiKey'],
            supportedConnectionModes: {
              web: ['hybrid'],
            },
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should fail when includeKeys is not defined but device mode is supported', async () => {
        const invalidDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            supportedConnectionModes: {
              web: ['device'],
            },
          },
        };

        await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow(
          /includeKeys must be defined and non-empty when at least one source type supports device\/hybrid mode/,
        );
      });

      it('should fail when includeKeys is empty but hybrid mode is supported', async () => {
        const invalidDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: [],
            supportedConnectionModes: {
              web: ['hybrid'],
              android: ['cloud'],
            },
          },
        };

        await expect(validateDestinationDefinitions(invalidDestDef)).rejects.toThrow(
          /includeKeys must be defined and non-empty when at least one source type supports device\/hybrid mode/,
        );
      });

      it('should pass when only cloud mode is supported without includeKeys', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            supportedConnectionModes: {
              web: ['cloud'],
            },
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when supportedConnectionModes is not defined', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {},
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });

      it('should pass when multiple sources support device mode and includeKeys is defined', async () => {
        const validDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: ['apiKey'],
            supportedConnectionModes: {
              web: ['device', 'cloud'],
              android: ['device'],
              ios: ['hybrid'],
            },
          },
        };

        await expect(validateDestinationDefinitions(validDestDef)).resolves.toBe(true);
      });
    });

    describe('Multiple rule violations', () => {
      it('should collect all validation errors', async () => {
        const invalidDestDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: ['apiKey', 'password'],
            secretKeys: ['password', 'token'],
          },
        };

        try {
          await validateDestinationDefinitions(invalidDestDef);
          fail('Expected validation to throw');
        } catch (error) {
          const errorMessage = error.message;
          // Should fail because password is in includeKeys but not in excludeKeys
          expect(errorMessage).toContain('Secret keys must not be exposed to client-side');
          expect(errorMessage).toContain('password');
        }
      });
    });

    describe('Edge cases with no config', () => {
      it('should handle destination definition with undefined config', async () => {
        const destDef = {
          name: 'TEST',
          displayName: 'Test',
          config: undefined,
        };

        await expect(validateDestinationDefinitions(destDef)).rejects.toThrow();
      });

      it('should handle destination definition with null config properties', async () => {
        const destDef = {
          name: 'TEST',
          displayName: 'Test',
          config: {
            includeKeys: null,
            excludeKeys: null,
            secretKeys: null,
          },
        };

        await expect(validateDestinationDefinitions(destDef)).resolves.toBe(true);
      });
    });
  });
});
