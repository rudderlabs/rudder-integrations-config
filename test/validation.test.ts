/* eslint-disable no-console */
/* eslint-disable max-len */
import fs from 'fs';
import path from 'path';
import Commander from 'commander';
import Ajv, { ValidateFunction } from 'ajv';
import addKeywords from 'ajv-keywords';
import ajvErrors from 'ajv-errors';
import {
  init,
  validateConfig,
  validateSourceDefinitions,
  validateDestinationDefinitions,
  validateAccountDefinitions,
} from '../src';

const command = new Commander.Command();
command
  .allowUnknownOption()
  .option('-d, --destinations <string>', 'Enter destination names separated by comma', 'all')
  .option('-s, --sources <string>', 'Enter source names separated by comma', 'all')
  .parse();

const cmdOpts = command.opts();

function getIntegrationNames(type: string) {
  const dirPath = path.resolve(`src/configurations/${type}`);
  return fs.readdirSync(dirPath).filter((file) => fs.statSync(`${dirPath}/${file}`).isDirectory());
}

function getAccountNames(type: string) {
  const dirPath = path.resolve(`src/configurations/${type}`);
  const integrations = getIntegrationNames(type);
  const accounts: string[] = [];

  integrations.forEach((integration) => {
    const accountsPath = path.join(dirPath, integration, 'accounts');
    if (fs.existsSync(accountsPath) && fs.statSync(accountsPath).isDirectory()) {
      const accountNames = fs.readdirSync(accountsPath);
      accountNames.forEach((account) => {
        const accountDbConfigPath = path.join(accountsPath, account, 'db-config.json');
        if (fs.existsSync(accountDbConfigPath)) {
          accounts.push(`${integration}/${account}`);
        }
      });
    }
  });

  return accounts;
}

function getIntegrationData(name: string, type: string): Record<string, unknown>[] {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let intgData: any;
  try {
    intgData = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, `./data/validation/${type}/${name}.json`), 'utf-8'),
    );
  } catch (e) {
    // console.error(e);
    // console.error(`Unable to load test data for: "${name}" (${type})`);
  }
  return intgData;
}

function getMinimalDestinationDefinition(hidden?: unknown) {
  return {
    name: 'TEST_DESTINATION',
    displayName: 'Test Destination',
    version: '1.0',
    config: {
      supportedSourceTypes: ['web'],
      destConfig: {
        defaultConfig: ['testConfig'],
      },
    },
    ...(hidden !== undefined && {
      options: {
        hidden,
      },
    }),
  };
}

function getMinimalSourceDefinition(hidden?: unknown) {
  return {
    name: 'test_source',
    displayName: 'Test Source',
    type: 'cloud',
    ...(hidden !== undefined && {
      options: {
        hidden,
      },
    }),
  };
}

function getMinimalAccountDefinition(hidden?: unknown) {
  return {
    name: 'TEST_ACCOUNT',
    type: 'test',
    category: 'destination',
    authenticationType: 'oauth',
    config: {
      optionFields: ['region'],
      refreshOAuthToken: true,
    },
    ...(hidden !== undefined && {
      displayOptions: {
        hidden,
      },
    }),
  };
}

let destList: string[] = [];
if (cmdOpts.destinations !== 'all') {
  destList = cmdOpts.destinations
    .split(',')
    .map((x: string) => x.trim())
    .filter((x: string) => x);
  console.log(`Destinations specified: ${destList}`);
} else {
  destList = getIntegrationNames('destinations');
}
const destTcData: Record<string, Record<string, unknown>[]> = {};
destList.forEach((d) => {
  const intgData = getIntegrationData(d, 'destinations');
  if (intgData) destTcData[d] = intgData;
});

let srcList: string[] = [];
if (cmdOpts.sources !== 'all') {
  srcList = cmdOpts.sources
    .split(',')
    .map((x: string) => x.trim())
    .filter((x: string) => x);
  console.log(`Sources specified: ${srcList}`);
} else {
  srcList = getIntegrationNames('sources');
}
const srcTcData: Record<string, Record<string, unknown>[]> = {};
srcList.forEach((s) => {
  const intgData = getIntegrationData(s, 'sources');
  if (intgData) srcTcData[s] = intgData;
});

function expectValidationError(
  validation: Promise<boolean>,
  expected: string,
  exact = true,
): Promise<void> {
  const matcher = expect(validation).rejects;
  return exact ? matcher.toThrow(new Error(expected)) : matcher.toThrow(expected);
}

async function getSourceDefinitionConfig(srcName: string) {
  const dirPath = path.resolve(`src/configurations/sources/${srcName}`);
  const configPath = `${dirPath}/db-config.json`;
  return import(configPath);
}

async function getAccountDefinitionConfig(
  integrationName: string,
  accountName: string,
  type: string,
) {
  const dirPath = path.resolve(
    `src/configurations/${type}/${integrationName}/accounts/${accountName}`,
  );
  if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
    const accountConfig = await import(path.join(dirPath, 'db-config.json'));
    return accountConfig.default;
  }

  throw new Error(`Account configuration not found for ${integrationName}/${accountName}`);
}

function getAccountDefinitionSchema(integrationName: string, accountName: string, type: string) {
  const schemaPath = path.resolve(
    `src/configurations/${type}/${integrationName}/accounts/${accountName}/schema.json`,
  );
  return JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));
}

// Mirrors the ajv configuration config-backend uses when validating an account
// payload against an account definition's schema. Deliberately no `coerceTypes`,
// so a stringified port stays a type error here exactly as it is in production.
function compileAccountSchema(schema: unknown) {
  const ajv = new Ajv({ allErrors: true, useDefaults: true, strict: false });
  return ajv.compile(schema as Record<string, unknown>);
}

// Mirrors config-backend `createAjv` (src/validations/configValidationErrors.ts), which loads
// ajv-errors, so an `errorMessage` asserted here is the text config-backend returns.
function compileAccountSchemaWithErrorMessages(schema: unknown): ValidateFunction {
  const ajv = new Ajv({
    allErrors: true,
    useDefaults: true,
    strict: false,
    strictSchema: false,
    strictRequired: false,
    strictNumbers: true,
    strictTypes: true,
    strictTuples: true,
  });
  addKeywords(ajv, ['uniqueItemProperties']);
  ajvErrors(ajv);
  return ajv.compile(schema as Record<string, unknown>);
}

async function getDestinationDefinitionConfig(destName: string) {
  const dirPath = path.resolve(`src/configurations/destinations/${destName}`);
  const configPath = `${dirPath}/db-config.json`;
  const config = await import(configPath);
  return config.default;
}

const dests = getIntegrationNames('destinations');
const sources = getIntegrationNames('sources');

describe('Core Tests', () => {
  it('If invalid integration name is provide, throw error', () => {
    expect(() => {
      validateConfig('', {}, 'destinations', true);
    }).toThrow('Missing definitionName');
  });

  it('If unknown integration name is provided, throw error', async () => {
    await init();

    const invalidIntg = 'INVALID_INTEGRATION_NAME';
    expect(() => {
      validateConfig(invalidIntg, {}, 'destinations', true);
    }).toThrow(`No validation method found for definition ${invalidIntg}`);
  });

  it('If unknown integration name is provided and throw errors flag is disabled, no error should be thrown', async () => {
    await init();

    const invalidIntg = 'INVALID_INTEGRATION_NAME';
    expect(() => {
      validateConfig(invalidIntg, {}, 'destinations');
    }).not.toThrow();
  });
});

describe('Validation Tests', () => {
  beforeAll(async () => {
    await init();
  });

  // Destination tests
  Object.keys(destTcData).forEach((dest: string, destIdx: number) => {
    describe(`${destIdx + 1}. Destination - ${dest}`, () => {
      destTcData[dest].forEach((td: Record<string, unknown>, tcIdx: number) => {
        it(`TC ${tcIdx + 1}${td.testTitle ? ` - ${td.testTitle}` : ''}`, async () => {
          if (td.result === true) {
            expect(
              validateConfig(dest, td.config as Record<string, unknown>, 'destinations', true),
            ).toBeUndefined();
          } else {
            expect(() => {
              validateConfig(dest, td.config as Record<string, unknown>, 'destinations', true);
            }).toThrow(JSON.stringify(td.err));
          }
        });
      });
    });
  });

  it('Customer.io applies v2 as the default API version when omitted', () => {
    const config: Record<string, unknown> = {
      apiKey: 'dummy-test-value',
      siteID: 'dummy-test-value',
      datacenter: 'US',
      userIdIdentifierType: 'id',
    };

    expect(validateConfig('customerio', config, 'destinations', true)).toBeUndefined();
    expect(config.apiVersion).toBe('v2');
  });

  const warehouseDestinationNames = [
    'azure_datalake',
    'azure_synapse',
    'bq',
    'clickhouse',
    'deltalake',
    'gcs_datalake',
    'microsoft_fabric',
    'mssql',
    'postgres',
    'rs',
    's3_datalake',
    'snowflake',
  ];

  const getWarehouseBaseConfig = (dest: string): Record<string, unknown> => {
    const validCase = getIntegrationData(dest, 'destinations')?.find((td) => td.result === true);
    if (!validCase) {
      throw new Error(`Missing valid test fixture for warehouse destination: ${dest}`);
    }
    return validCase.config as Record<string, unknown>;
  };

  describe('Warehouse sync frequency validation', () => {
    warehouseDestinationNames.forEach((dest) => {
      it(`${dest} accepts 10-minute sync frequency and rejects invalid frequency`, () => {
        const baseConfig = getWarehouseBaseConfig(dest);
        expect(() => {
          validateConfig(dest, { ...baseConfig, syncFrequency: '10' }, 'destinations', true);
        }).not.toThrow();
        expect(() => {
          validateConfig(dest, { ...baseConfig, syncFrequency: '11' }, 'destinations', true);
        }).toThrow();
      });
    });
  });

  describe('Warehouse backward-compatibility flag validation', () => {
    const backwardCompatibilityFlags = ['allowUsersContextTraits', 'underscoreDivideNumbers'];
    // Every destination declaring the flags, not just those with a sync frequency.
    const backwardCompatibilityDestinationNames = [
      ...warehouseDestinationNames.filter((dest) => dest !== 'microsoft_fabric'),
      'bqstream_all_events',
      'snowpipe_streaming',
    ];

    backwardCompatibilityDestinationNames.forEach((dest) => {
      backwardCompatibilityFlags.forEach((flag) => {
        it(`${dest} accepts boolean ${flag} and rejects non-boolean values`, () => {
          const baseConfig = getWarehouseBaseConfig(dest);

          [true, false].forEach((value) => {
            expect(() => {
              validateConfig(dest, { ...baseConfig, [flag]: value }, 'destinations', true);
            }).not.toThrow();
          });

          ['false', 0, null].forEach((value) => {
            expect(() => {
              validateConfig(dest, { ...baseConfig, [flag]: value }, 'destinations', true);
            }).toThrow(`${flag} must be boolean`);
          });
        });
      });

      it(`${dest} omitting the backward-compatibility flags is valid`, () => {
        // Existing stored configs predate these flags, so absence must stay valid.
        const configWithoutFlags = { ...getWarehouseBaseConfig(dest) };
        backwardCompatibilityFlags.forEach((flag) => delete configWithoutFlags[flag]);

        expect(() => {
          validateConfig(dest, configWithoutFlags, 'destinations', true);
        }).not.toThrow();
      });
    });
  });

  // Source tests
  Object.keys(srcTcData).forEach((src: string, srcIdx: number) => {
    describe(`${srcIdx + 1}. Source - ${src}`, () => {
      srcTcData[src].forEach((td: Record<string, unknown>, tcIdx: number) => {
        it(`TC ${tcIdx + 1}${td.testTitle ? ` - ${td.testTitle}` : ''}`, async () => {
          if (td.result === true) {
            expect(
              validateConfig(src, td.config as Record<string, unknown>, 'sources', true),
            ).toBeUndefined();
          } else {
            expect(() => {
              validateConfig(src, td.config as Record<string, unknown>, 'sources', true);
            }).toThrow(JSON.stringify(td.err));
          }
        });
      });
    });
  });
});

describe('Destination Definition validation tests', () => {
  dests.forEach((dest) => {
    it(`${dest} - destination definition test`, async () => {
      const destDefConfig = await getDestinationDefinitionConfig(dest);
      await expect(validateDestinationDefinitions(destDefConfig)).resolves.toEqual(true);
    });
  });

  const malformedDestDefConfigs = [
    {
      description: 'missing "name" and "displayName" properties',
      input: {
        version: '1.0',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
        },
      },
      expected:
        '[" must have required property \'name\'"," must have required property \'displayName\'"]',
    },
    {
      description: 'missing "version" property',
      input: {
        name: 'test',
        displayName: 'Test',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
        },
      },
      expected: '[" must have required property \'version\'"]',
    },
    {
      description: 'supportsVisualMapperV2 cannot be combined with VDMv1 mapper flags',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportsVisualMapperV2: true,
          supportsBlankAudienceCreation: true,
        },
      },
      expected: '["config must NOT be valid","config must match \\"then\\" schema"]',
    },
    {
      description: 'hybridModeCloudEventsFilter is not a valid map',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: [],
        },
      },
      expected: '["config.hybridModeCloudEventsFilter must be object"]',
    },
    {
      description: 'hybridModeCloudEventsFilter is empty map',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: {},
        },
      },
      expected: '["config.hybridModeCloudEventsFilter must NOT have fewer than 1 properties"]',
    },
    {
      description: 'hybridModeCloudEventsFilter has unsupported source types',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: {
            web: {
              messageType: ['track'],
            },
            differentSourceType: {
              messageType: ['page', 'group'],
            },
          },
        },
      },
      expected: '["config.hybridModeCloudEventsFilter must NOT have additional properties"]',
    },
    {
      description: 'hybridModeCloudEventsFilter has empty map for web source type',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: {
            web: {},
          },
        },
      },
      expected:
        '["config.hybridModeCloudEventsFilter.web must have required property \'messageType\'"]',
    },
    {
      description: 'hybridModeCloudEventsFilter has invalid fields for web source type',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: {
            web: {
              randomType: ['random_1', 'random_2'],
            },
          },
        },
      },
      expected:
        '["config.hybridModeCloudEventsFilter.web must have required property \'messageType\'","config.hybridModeCloudEventsFilter.web must NOT have additional properties"]',
    },
    {
      description:
        'hybridModeCloudEventsFilter has invalid values for "messageType" for web source type',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedSourceTypes: ['web'],
          hybridModeCloudEventsFilter: {
            web: {
              messageType: 'track',
            },
          },
        },
      },
      expected: '["config.hybridModeCloudEventsFilter.web.messageType must be array"]',
    },
    {
      description: 'hidden gate flag item is missing "value"',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG' }],
        },
      }),
      expected: "must have required property 'value'",
      exact: false,
    },
    {
      description: 'hidden gate flag item is missing "name"',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [{ value: true }],
        },
      }),
      expected: "must have required property 'name'",
      exact: false,
    },
    {
      description: 'hidden gate with multiple flags is missing "condition"',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [
            { name: 'AMP_TEST_FLAG', value: true },
            { name: 'TEST_BILLING_FEATURE', value: true },
          ],
        },
      }),
      expected: "must have required property 'condition'",
      exact: false,
    },
    {
      description: 'hidden gate has an unknown property',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: true }],
          unknownProperty: true,
        },
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'hidden gate flag item has an unknown property',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: true, unknownProperty: true }],
        },
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'hidden object mixes gate and legacy feature flag fields',
      input: getMinimalDestinationDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: false }],
        },
        featureFlagName: 'AMP_TEST_FLAG',
        featureFlagValue: false,
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'unknown top-level property is rejected',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        unknownTopLevelKey: true,
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
        },
      },
      expected: '[" must NOT have additional properties"]',
    },
    {
      description: 'unknown property under config.auth is rejected',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
          auth: {
            type: 'OAuth',
            unknownAuthKey: true,
          },
        },
      },
      expected: '["config.auth must NOT have additional properties"]',
    },
    {
      description: 'unknown property under config.supportedAccountDefinitions is rejected',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
          supportedAccountDefinitions: {
            rudderAccountId: ['someAccountDefinitionId'],
            unknownAccountKey: ['x'],
          },
        },
      },
      expected: '["config.supportedAccountDefinitions must NOT have additional properties"]',
    },
    {
      description: 'unknown property under options.hidden object variant is rejected',
      input: {
        name: 'test',
        displayName: 'Test',
        version: '1.0',
        config: {
          supportedSourceTypes: ['web'],
          destConfig: {
            defaultConfig: ['temp'],
          },
        },
        options: {
          hidden: {
            featureFlagName: 'AMP_test',
            featureFlagValue: false,
            unknownHiddenKey: 'x',
          },
        },
      },
      expected: 'must NOT have additional properties',
      exact: false,
    },
  ];

  it.each(malformedDestDefConfigs)('$description', async (testCase) => {
    await expectValidationError(
      validateDestinationDefinitions(testCase.input),
      testCase.expected,
      testCase.exact,
    );
  });

  it('accepts Visual Mapper V2 with legacy audience support', async () => {
    const destinationDefinition = getMinimalDestinationDefinition();

    await expect(
      validateDestinationDefinitions({
        ...destinationDefinition,
        config: {
          ...destinationDefinition.config,
          supportsVisualMapperV2: true,
          isAudienceSupported: true,
        },
      }),
    ).resolves.toEqual(true);
  });

  it('accepts boolean hidden', async () => {
    await expect(
      validateDestinationDefinitions(getMinimalDestinationDefinition(true)),
    ).resolves.toEqual(true);
  });

  it('rejects legacy hidden feature flag object', async () => {
    await expectValidationError(
      validateDestinationDefinitions(
        getMinimalDestinationDefinition({
          featureFlagName: 'AMP_TEST_FLAG',
          featureFlagValue: false,
        }),
      ),
      "must have required property 'gate'",
      false,
    );
  });

  it('accepts hidden gate with a single flag and no condition', async () => {
    await expect(
      validateDestinationDefinitions(
        getMinimalDestinationDefinition({
          gate: {
            flags: [{ name: 'AMP_TEST_FLAG', value: false }],
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('accepts hidden gate with a single flag and condition', async () => {
    await expect(
      validateDestinationDefinitions(
        getMinimalDestinationDefinition({
          gate: {
            flags: [{ name: 'AMP_TEST_FLAG', value: false }],
            condition: 'and',
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('accepts hidden gate with two flags and condition', async () => {
    await expect(
      validateDestinationDefinitions(
        getMinimalDestinationDefinition({
          gate: {
            flags: [
              { name: 'AMP_TEST_FLAG', value: false },
              { name: 'TEST_BILLING_FEATURE', value: false },
            ],
            condition: 'and',
          },
        }),
      ),
    ).resolves.toEqual(true);
  });
});

describe('Source Definition validation tests', () => {
  sources.forEach((src) => {
    it(`${src} - source definition test`, async () => {
      const srcDefConfig = await getSourceDefinitionConfig(src);
      await expect(validateSourceDefinitions(srcDefConfig)).resolves.toEqual(true);
    });
  });

  const malformedSrcDefConfigs = [
    {
      description: 'missing "name" and "displayName" properties',
      input: {
        type: 'cloud',
        category: 'webhook',
      },
      expected:
        '[" must have required property \'name\'"," must have required property \'displayName\'"]',
    },
    {
      description: 'internalSecretKeys with non-string items',
      input: {
        name: 'test_source',
        displayName: 'Test Source',
        type: 'cloud',
        category: 'webhook',
        options: {
          internalSecretKeys: [123, 'validString'],
        },
      },
      expected: '["options.internalSecretKeys.0 must be string"]',
    },
    {
      description: 'internalSecretKeys with duplicate items',
      input: {
        name: 'test_source',
        displayName: 'Test Source',
        type: 'cloud',
        category: 'webhook',
        options: {
          internalSecretKeys: ['apiKey', 'apiKey'],
        },
      },
      expected:
        '["options.internalSecretKeys must NOT have duplicate items (items ## 1 and 0 are identical)"]',
    },
    {
      description: 'hidden gate flag item is missing "value"',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG' }],
        },
      }),
      expected: "must have required property 'value'",
      exact: false,
    },
    {
      description: 'hidden gate flag item is missing "name"',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [{ value: true }],
        },
      }),
      expected: "must have required property 'name'",
      exact: false,
    },
    {
      description: 'hidden gate with multiple flags is missing "condition"',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [
            { name: 'AMP_TEST_FLAG', value: true },
            { name: 'TEST_BILLING_FEATURE', value: true },
          ],
        },
      }),
      expected: "must have required property 'condition'",
      exact: false,
    },
    {
      description: 'hidden gate has an unknown property',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: true }],
          unknownProperty: true,
        },
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'hidden gate flag item has an unknown property',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: true, unknownProperty: true }],
        },
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'hidden object mixes gate and legacy feature flag fields',
      input: getMinimalSourceDefinition({
        gate: {
          flags: [{ name: 'AMP_TEST_FLAG', value: false }],
        },
        featureFlagName: 'AMP_TEST_FLAG',
        featureFlagValue: false,
      }),
      expected: 'must NOT have additional properties',
      exact: false,
    },
    {
      description: 'config.supportedAccountDefinitions.rudderAccountId with non-array value',
      input: {
        name: 'test_source',
        displayName: 'Test Source',
        type: 'cloud',
        category: 'webhook',
        config: {
          supportedAccountDefinitions: {
            rudderAccountId: 'SOURCE_TEST_OAUTH',
          },
        },
      },
      expected: '["config.supportedAccountDefinitions.rudderAccountId must be array"]',
    },
    {
      description: 'config.supportedAccountDefinitions.rudderAccountId with empty array',
      input: {
        name: 'test_source',
        displayName: 'Test Source',
        type: 'cloud',
        category: 'webhook',
        config: {
          supportedAccountDefinitions: {
            rudderAccountId: [],
          },
        },
      },
      expected:
        '["config.supportedAccountDefinitions.rudderAccountId must NOT have fewer than 1 items"]',
    },
    {
      description: 'config.supportedAccountDefinitions with empty object',
      input: {
        name: 'test_source',
        displayName: 'Test Source',
        type: 'cloud',
        category: 'webhook',
        config: {
          supportedAccountDefinitions: {},
        },
      },
      expected: '["config.supportedAccountDefinitions must NOT have fewer than 1 properties"]',
    },
  ];

  it.each(malformedSrcDefConfigs)('$description', async (testCase) => {
    await expectValidationError(
      validateSourceDefinitions(testCase.input),
      testCase.expected,
      testCase.exact,
    );
  });

  it('accepts boolean hidden', async () => {
    await expect(validateSourceDefinitions(getMinimalSourceDefinition(true))).resolves.toEqual(
      true,
    );
  });

  it('rejects legacy hidden feature flag object', async () => {
    await expectValidationError(
      validateSourceDefinitions(
        getMinimalSourceDefinition({
          featureFlagName: 'AMP_TEST_FLAG',
          featureFlagValue: false,
        }),
      ),
      "must have required property 'gate'",
      false,
    );
  });

  it('accepts hidden gate with a single flag and no condition', async () => {
    await expect(
      validateSourceDefinitions(
        getMinimalSourceDefinition({
          gate: {
            flags: [{ name: 'AMP_TEST_FLAG', value: false }],
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('accepts hidden gate with a single flag and condition', async () => {
    await expect(
      validateSourceDefinitions(
        getMinimalSourceDefinition({
          gate: {
            flags: [{ name: 'AMP_TEST_FLAG', value: false }],
            condition: 'and',
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('accepts hidden gate with two flags and condition', async () => {
    await expect(
      validateSourceDefinitions(
        getMinimalSourceDefinition({
          gate: {
            flags: [
              { name: 'AMP_TEST_FLAG', value: false },
              { name: 'TEST_BILLING_FEATURE', value: false },
            ],
            condition: 'and',
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('config.supportedAccountDefinitions.rudderAccountId with valid array value is accepted', async () => {
    const srcDefConfig = {
      name: 'test_source',
      displayName: 'Test Source',
      type: 'cloud',
      category: 'webhook',
      config: {
        supportedAccountDefinitions: {
          rudderAccountId: ['SOURCE_TEST_OAUTH'],
        },
      },
    };
    await expect(validateSourceDefinitions(srcDefConfig)).resolves.toEqual(true);
  });
});

describe('Account Definition validation tests', () => {
  const destinationAccounts = getAccountNames('destinations');
  destinationAccounts.forEach((account) => {
    const [integration, accountName] = account.split('/');
    it(`${integration}/${accountName} - account definition test`, async () => {
      const accDefConfig = await getAccountDefinitionConfig(
        integration,
        accountName,
        'destinations',
      );
      await expect(validateAccountDefinitions(accDefConfig)).resolves.toEqual(true);
    });
  });

  const sourceAccounts = getAccountNames('sources');
  sourceAccounts.forEach((account) => {
    const [integration, accountName] = account.split('/');
    it(`${integration}/${accountName} - account definition test`, async () => {
      const accDefConfig = await getAccountDefinitionConfig(integration, accountName, 'sources');
      await expect(validateAccountDefinitions(accDefConfig)).resolves.toEqual(true);
    });
  });

  // The `combinedSchema` if/then/else is the only thing binding an auth branch to the
  // credential it needs: the standalone `secretSchema` of these warehouse source accounts
  // accepts any object, and `scripts/validate_account_definitions.py` only walks
  // `src/configurations/destinations`, so nothing else in this repo exercises it.
  const accountSchemaMetaSchemaPath = path.resolve(
    'src/schemas/account/account-schema-schema.json',
  );

  const bigQueryWifPayload = () => ({
    options: {
      project: 'customer-project',
      authMethod: 'workloadIdentityFederation',
      workloadIdentityProjectNumber: '123456789012',
      workloadIdentityPoolId: 'rudderstack-pool',
      workloadIdentityProviderId: 'rudderstack-aws',
    },
    secret: {},
  });

  const bigQueryKeyPayload = () => ({
    options: {
      project: 'customer-project',
      authMethod: 'serviceAccountKey',
    },
    secret: { credentials: '{"type":"service_account"}' },
  });

  it('SOURCE_BIGQUERY account schema is valid against the account schema meta-schema', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const metaSchema = JSON.parse(fs.readFileSync(accountSchemaMetaSchemaPath, 'utf-8'));
    const validateAccountSchema = compileAccountSchema(metaSchema);

    const isValid = validateAccountSchema(accountSchema);
    expect(validateAccountSchema.errors ?? []).toEqual([]);
    expect(isValid).toBe(true);
    expect(accountSchema.combinedSchema).toBeDefined();
  });

  it('SOURCE_BIGQUERY combinedSchema accepts WIF, keyed, and legacy accounts', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);
    const validateOptions = compileAccountSchema(accountSchema.optionsSchema);
    const domainScopedWifOptions = {
      ...bigQueryWifPayload().options,
      project: 'example.com:analytics-prod-123456',
    };

    expect(validateCombined(bigQueryWifPayload())).toBe(true);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        secret: { credentials: '' },
      }),
    ).toBe(true);
    expect(validateCombined(bigQueryKeyPayload())).toBe(true);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: domainScopedWifOptions,
      }),
    ).toBe(true);
    expect(
      validateOptions({
        ...bigQueryKeyPayload().options,
        project: 'google.com:abc',
      }),
    ).toBe(true);
    expect(
      validateCombined({
        options: {
          project: 'legacy-project',
          serviceAccount: 'legacy@legacy-project.iam.gserviceaccount.com',
        },
        secret: { credentials: '{"type":"service_account"}' },
      }),
    ).toBe(true);
    expect(
      validateCombined({
        ...bigQueryKeyPayload(),
        options: { ...bigQueryKeyPayload().options, project: 'google.com:abc' },
      }),
    ).toBe(true);
  });

  it.each([
    'workloadIdentityProjectNumber',
    'workloadIdentityPoolId',
    'workloadIdentityProviderId',
  ])('SOURCE_BIGQUERY WIF requires %s', (field) => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);
    const payload = bigQueryWifPayload();
    delete payload.options[field as keyof typeof payload.options];

    expect(validateCombined(payload)).toBe(false);
  });

  it.each([
    'workloadIdentityProjectNumber',
    'workloadIdentityPoolId',
    'workloadIdentityProviderId',
  ])('SOURCE_BIGQUERY WIF rejects an empty %s', (field) => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: { ...bigQueryWifPayload().options, [field]: '' },
      }),
    ).toBe(false);
  });

  it('SOURCE_BIGQUERY combinedSchema requires non-empty credentials on keyed and legacy accounts', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(validateCombined({ ...bigQueryKeyPayload(), secret: {} })).toBe(false);
    expect(validateCombined({ options: { project: 'legacy-project' }, secret: {} })).toBe(false);
    expect(validateCombined({ ...bigQueryKeyPayload(), secret: { credentials: '' } })).toBe(false);
  });

  it('SOURCE_BIGQUERY combinedSchema rejects unknown authentication methods', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryKeyPayload(),
        options: { ...bigQueryKeyPayload().options, authMethod: 'workloadIdentity' },
      }),
    ).toBe(false);
  });

  it('SOURCE_BIGQUERY combinedSchema ignores inactive WIF values on keyed and legacy accounts', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);
    const validateOptions = compileAccountSchema(accountSchema.optionsSchema);
    const inactiveWifValues = {
      workloadIdentityProjectNumber: 'not-a-number',
      workloadIdentityPoolId: 'INVALID POOL',
      workloadIdentityProviderId: 'INVALID PROVIDER',
      workloadIdentityTargetServiceAccount: 'not-a-service-account',
    };

    expect(
      validateCombined({
        ...bigQueryKeyPayload(),
        options: { ...bigQueryKeyPayload().options, ...inactiveWifValues },
      }),
    ).toBe(true);
    expect(
      validateOptions({
        ...bigQueryKeyPayload().options,
        ...inactiveWifValues,
      }),
    ).toBe(true);
    expect(
      validateCombined({
        options: { project: 'legacy-project', ...inactiveWifValues },
        secret: { credentials: '{"type":"service_account"}' },
      }),
    ).toBe(true);
  });

  it('SOURCE_BIGQUERY combinedSchema rejects stored service-account credentials for WIF accounts', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          serviceAccount: 'stale@customer-project.iam.gserviceaccount.com',
        },
        secret: { credentials: '{"type":"service_account"}' },
      }),
    ).toBe(false);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        secret: { unexpectedSecret: 'must-not-be-stored' },
      }),
    ).toBe(false);
  });

  it('SOURCE_BIGQUERY WIF fields use the destination-compatible identifier patterns', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityProviderId: '1234',
        },
      }),
    ).toBe(true);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityProviderId: 'gcp-provider',
        },
      }),
    ).toBe(false);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityProjectNumber: 'project-number',
        },
      }),
    ).toBe(false);
    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityPoolId: 'gcp-pool',
        },
      }),
    ).toBe(false);
  });

  it.each([
    'rudderstack@customer-project.iam.gserviceaccount.com',
    'sa@proj.example.com.iam.gserviceaccount.com',
    '123-compute@developer.gserviceaccount.com',
    'app@appspot.gserviceaccount.com',
  ])('SOURCE_BIGQUERY WIF accepts target service account %s', (targetServiceAccount) => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityTargetServiceAccount: targetServiceAccount,
        },
      }),
    ).toBe(true);
  });

  it('SOURCE_BIGQUERY WIF accepts an empty target service account for direct federation', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityTargetServiceAccount: '',
        },
      }),
    ).toBe(true);
  });

  it.each([
    'sa@proj:evil.iam.gserviceaccount.com',
    'sa@proj/evil.iam.gserviceaccount.com',
    'sa@proj.iam.gserviceaccount.com?audience=attacker',
    'sa@proj.iam.gserviceaccount.com#fragment',
    'sa @proj.iam.gserviceaccount.com',
  ])('SOURCE_BIGQUERY WIF rejects invalid target service account %p', (targetServiceAccount) => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(
      validateCombined({
        ...bigQueryWifPayload(),
        options: {
          ...bigQueryWifPayload().options,
          workloadIdentityTargetServiceAccount: targetServiceAccount,
        },
      }),
    ).toBe(false);
  });

  it('SOURCE_BIGQUERY db-config option and secret fields match its schema properties', async () => {
    const accountConfig = await getAccountDefinitionConfig(
      'bigquery',
      'SOURCE_BIGQUERY',
      'sources',
    );
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');

    expect([...accountConfig.config.optionFields].sort()).toEqual(
      Object.keys(accountSchema.optionsSchema.properties).sort(),
    );
    expect([...accountConfig.config.secretFields].sort()).toEqual(
      Object.keys(accountSchema.secretSchema.properties).sort(),
    );
  });

  it('SOURCE_BIGQUERY UI gates WIF fields while retaining key fields when the flag is off', () => {
    const uiConfigPath = path.resolve('src/configurations/sources/bigquery/ui-config.json');
    const uiConfig = JSON.parse(fs.readFileSync(uiConfigPath, 'utf-8'));
    const { fields } = uiConfig.uiConfig[0];
    const fieldByValue = Object.fromEntries(
      fields
        .filter((field: { value: string }) => field.value !== 'project')
        .map((field: { value: string }) => [field.value, field]),
    );
    const projectFields = fields.filter((field: { value: string }) => field.value === 'project');
    expect(projectFields).toHaveLength(2);
    const keyProjectField = projectFields.find((field: { readOnly?: boolean }) => field.readOnly);
    const wifProjectField = projectFields.find(
      (field: { readOnly?: boolean }) => field.readOnly !== true,
    );
    expect(keyProjectField).toBeDefined();
    expect(wifProjectField).toBeDefined();
    const featureFlag = 'AMP_enable-bigquery-source-workload-identity-federation';

    const enabledFeatureFlag = [{ configKey: featureFlag, value: true }];
    const disabledFeatureFlag = [{ configKey: featureFlag }];
    const wifFieldPrerequisites = {
      fields: [{ configKey: 'authMethod', value: 'workloadIdentityFederation' }],
      featureFlags: enabledFeatureFlag,
    };
    const keyFieldPrerequisites = {
      fields: [{ configKey: 'authMethod', value: 'serviceAccountKey' }],
      featureFlags: disabledFeatureFlag,
      prerequisitesCondition: 'or',
    };

    expect(fieldByValue.authMethod.preRequisites).toEqual({
      featureFlags: enabledFeatureFlag,
    });
    expect(fieldByValue.authMethod.preRequisiteFeatureFlag).toBeUndefined();
    expect(fieldByValue.authMethod.defaultOption.value).toBe('serviceAccountKey');
    expect(fieldByValue.authMethod.footerNote).not.toContain('Workload Identity Federation');
    expect(fieldByValue.authMethod.footerNote).not.toContain(
      'assumed-role/data-plane-service-account/<workspaceID>',
    );
    expect(fieldByValue.workloadIdentityProjectNumber.footerNote).toContain(
      'Workload Identity Federation',
    );
    expect(fieldByValue.workloadIdentityProjectNumber.footerNote).toContain(
      'assumed-role/data-plane-service-account/<workspaceID>',
    );
    expect(fieldByValue.workloadIdentityProjectNumber.footerNote).toContain('not the whole role');
    expect(fieldByValue.workloadIdentityProjectNumber.footerNote).toContain(
      'optionally impersonate your service account',
    );
    expect(fieldByValue.credentials.preRequisites).toEqual(keyFieldPrerequisites);
    expect(fieldByValue.serviceAccount.preRequisites).toEqual(
      fieldByValue.credentials.preRequisites,
    );
    expect(keyProjectField.preRequisites).toEqual(keyFieldPrerequisites);
    expect(wifProjectField.preRequisites).toEqual(wifFieldPrerequisites);

    const { preRequisites: _keyProjectPrerequisites, ...keyProjectDevelopShape } = keyProjectField;
    expect(JSON.stringify(keyProjectDevelopShape)).toBe(
      JSON.stringify({
        type: 'textInput',
        label: 'Project ID',
        labelNote: 'GCP Project ID where your BigQuery database is located.',
        value: 'project',
        regex: '^(.{0,100})$',
        regexErrorMessage: 'Invalid Value',
        required: true,
        infoTooltip: 'Inferred from project_id field in the credentials settings.',
        addInAccountSummary: true,
        readOnly: true,
        obtainValueFromField: {
          name: 'credentials',
          key: 'project_id',
        },
      }),
    );
    expect(wifProjectField).toMatchObject({
      type: 'textInput',
      value: 'project',
      required: true,
      regex: '^(?:[a-z][a-z0-9.-]*[a-z0-9]:)?[a-z][a-z0-9-]{4,28}[a-z0-9]$',
    });

    [
      'workloadIdentityProjectNumber',
      'workloadIdentityPoolId',
      'workloadIdentityProviderId',
      'workloadIdentityTargetServiceAccount',
    ].forEach((fieldName) => {
      expect(fieldByValue[fieldName].preRequisites).toEqual(wifFieldPrerequisites);
      expect(fieldByValue[fieldName].preRequisiteFeatureFlag).toBeUndefined();
      expect(fieldByValue[fieldName].preRequisiteField).toBeUndefined();
    });
    expect(fieldByValue.workloadIdentityTargetServiceAccount.required).toBe(false);

    const isVisible = (
      field: {
        preRequisites?: {
          fields?: Array<{ configKey: string; value: unknown }>;
          featureFlags?: Array<{ configKey: string; value?: unknown }>;
          prerequisitesCondition?: string;
        };
      },
      authMethod: string | undefined,
      featureEnabled: boolean | undefined,
    ) => {
      if (!field.preRequisites) return true;
      const checks = [
        ...(field.preRequisites.fields ?? []).map(
          ({ configKey, value }) => configKey === 'authMethod' && value === authMethod,
        ),
        ...(field.preRequisites.featureFlags ?? []).map(({ configKey, value }) => {
          if (configKey !== featureFlag) return false;
          return value === undefined ? !featureEnabled : value === featureEnabled;
        }),
      ];
      return field.preRequisites.prerequisitesCondition === 'or'
        ? checks.some(Boolean)
        : checks.every(Boolean);
    };
    const visibleFields = (authMethod: string | undefined, featureEnabled: boolean | undefined) =>
      fields
        .filter((field: { value: string }) => isVisible(field, authMethod, featureEnabled))
        .map((field: { value: string; readOnly?: boolean }) => {
          if (field.value !== 'project') return field.value;
          return field.readOnly ? 'keyProject' : 'wifProject';
        });

    const states = [
      {
        name: 'missing flag with service account key',
        authMethod: 'serviceAccountKey',
        featureEnabled: undefined,
        expected: ['credentials', 'keyProject', 'serviceAccount'],
      },
      {
        name: 'missing flag with workload identity federation',
        authMethod: 'workloadIdentityFederation',
        featureEnabled: undefined,
        expected: ['credentials', 'keyProject', 'serviceAccount'],
      },
      {
        name: 'disabled flag with service account key',
        authMethod: 'serviceAccountKey',
        featureEnabled: false,
        expected: ['credentials', 'keyProject', 'serviceAccount'],
      },
      {
        name: 'disabled flag with workload identity federation',
        authMethod: 'workloadIdentityFederation',
        featureEnabled: false,
        expected: ['credentials', 'keyProject', 'serviceAccount'],
      },
      {
        name: 'enabled flag with service account key',
        authMethod: 'serviceAccountKey',
        featureEnabled: true,
        expected: ['authMethod', 'credentials', 'keyProject', 'serviceAccount'],
      },
      {
        name: 'enabled flag with workload identity federation',
        authMethod: 'workloadIdentityFederation',
        featureEnabled: true,
        expected: [
          'authMethod',
          'wifProject',
          'workloadIdentityProjectNumber',
          'workloadIdentityPoolId',
          'workloadIdentityProviderId',
          'workloadIdentityTargetServiceAccount',
        ],
      },
      {
        name: 'legacy edit without auth method or feature flag',
        authMethod: undefined,
        featureEnabled: undefined,
        expected: ['credentials', 'keyProject', 'serviceAccount'],
      },
    ];
    states.forEach(({ name, authMethod, featureEnabled, expected }) => {
      const visible = visibleFields(authMethod, featureEnabled);
      expect({ name, visible }).toEqual({ name, visible: expected });
      const visibleWifExplanations = fields.filter(
        (field: { footerNote?: string }) =>
          isVisible(field, authMethod, featureEnabled) &&
          field.footerNote?.includes('assumed-role/data-plane-service-account/<workspaceID>'),
      );
      expect({ name, wifExplanationCount: visibleWifExplanations.length }).toEqual({
        name,
        wifExplanationCount:
          authMethod === 'workloadIdentityFederation' && featureEnabled === true ? 1 : 0,
      });
      const visibleProjectFields = projectFields.filter((field: { value: string }) =>
        isVisible(field, authMethod, featureEnabled),
      );
      expect({ name, projectFieldCount: visibleProjectFields.length }).toEqual({
        name,
        projectFieldCount: 1,
      });
      expect({ name, projectRequired: visibleProjectFields[0].required }).toEqual({
        name,
        projectRequired: true,
      });
    });
  });

  it('SOURCE_BIGQUERY WIF UI regexes match the combined schema patterns', () => {
    const accountSchema = getAccountDefinitionSchema('bigquery', 'SOURCE_BIGQUERY', 'sources');
    const uiConfigPath = path.resolve('src/configurations/sources/bigquery/ui-config.json');
    const uiConfig = JSON.parse(fs.readFileSync(uiConfigPath, 'utf-8'));
    const projectFields = uiConfig.uiConfig[0].fields.filter(
      (field: { value: string }) => field.value === 'project',
    );
    const fieldByValue = Object.fromEntries(
      uiConfig.uiConfig[0].fields
        .filter((field: { value: string }) => field.value !== 'project')
        .map((field: { value: string }) => [field.value, field]),
    );
    const wifProperties = accountSchema.combinedSchema.then.properties.options.properties;
    const wifProjectField = projectFields.find(
      (field: { readOnly?: boolean }) => field.readOnly !== true,
    );

    expect(accountSchema.optionsSchema.properties.project.pattern).toBe(
      '^[a-z][a-z0-9.:-]{4,28}[a-z0-9]$',
    );
    expect(accountSchema.combinedSchema.else.properties.options.properties.project.pattern).toBe(
      accountSchema.optionsSchema.properties.project.pattern,
    );
    expect(wifProjectField.regex).toBe(
      accountSchema.combinedSchema.then.properties.options.properties.project.pattern,
    );

    [
      'workloadIdentityProjectNumber',
      'workloadIdentityPoolId',
      'workloadIdentityProviderId',
      'workloadIdentityTargetServiceAccount',
    ].forEach((fieldName) => {
      expect(fieldByValue[fieldName].regex).toBe(wifProperties[fieldName].pattern);
    });
  });

  // sqlconnect-go unmarshals the port into `Port int`, so the integer form is the only
  // one that survives a sync. The string form is a transitional allowance for the
  // rudder-iac fixture; a follow-up PR drops it once rudderlabs/rudder-iac#827 has merged.
  // Either way an out-of-range value is not a port and neither form should accept one.
  it('SOURCE_POSTGRES optionsSchema accepts both port forms and bounds each to 1-65535', () => {
    const accountSchema = getAccountDefinitionSchema('postgres', 'SOURCE_POSTGRES', 'sources');
    const validateOptions = compileAccountSchema(accountSchema.optionsSchema);
    const options = (port: unknown) => ({
      host: 'db.example.internal',
      dbname: 'analytics',
      user: 'rudder',
      sslMode: 'require',
      port,
    });

    expect(validateOptions(options(1))).toBe(true);
    expect(validateOptions(options('1'))).toBe(true);
    expect(validateOptions(options(5432))).toBe(true);
    expect(validateOptions(options('5432'))).toBe(true);
    expect(validateOptions(options(65535))).toBe(true);
    expect(validateOptions(options('65535'))).toBe(true);

    expect(validateOptions(options(0))).toBe(false);
    expect(validateOptions(options('0'))).toBe(false);
    expect(validateOptions(options(65536))).toBe(false);
    expect(validateOptions(options('99999'))).toBe(false);
    expect(validateOptions(options('00001'))).toBe(false);
    expect(validateOptions(options('5432abc'))).toBe(false);
  });

  const redshiftPasswordPayload = () => ({
    options: {
      host: 'examplecluster.abc123.us-east-1.redshift.amazonaws.com',
      port: 5439,
      user: 'rudder',
      dbname: 'analytics',
      sslMode: 'verify-full',
      authenticationType: 'password',
    },
    secret: { password: 'super-secret' },
  });

  const redshiftIamPayload = () => ({
    options: {
      user: 'rudder',
      dbname: 'analytics',
      sslMode: 'verify-full',
      authenticationType: 'iam',
      clusterIdentifier: 'examplecluster',
      region: 'us-east-1',
      roleARN: 'arn:aws:iam::123456789012:role/RudderStackRedshift',
    },
    secret: {},
  });

  it('SOURCE_REDSHIFT account schema is valid against the account schema meta-schema', () => {
    const accountSchema = getAccountDefinitionSchema('redshift', 'SOURCE_REDSHIFT', 'sources');
    const metaSchema = JSON.parse(fs.readFileSync(accountSchemaMetaSchemaPath, 'utf-8'));
    const validateAccountSchema = compileAccountSchema(metaSchema);

    const isValid = validateAccountSchema(accountSchema);
    expect(validateAccountSchema.errors ?? []).toEqual([]);
    expect(isValid).toBe(true);
    expect(accountSchema.combinedSchema).toBeDefined();
  });

  it('SOURCE_REDSHIFT combinedSchema accepts the password and iam auth branches', () => {
    const accountSchema = getAccountDefinitionSchema('redshift', 'SOURCE_REDSHIFT', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(validateCombined(redshiftPasswordPayload())).toBe(true);
    expect(validateCombined(redshiftIamPayload())).toBe(true);
  });

  it('SOURCE_REDSHIFT combinedSchema rejects credentials that do not match the auth branch', () => {
    const accountSchema = getAccountDefinitionSchema('redshift', 'SOURCE_REDSHIFT', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    // iam never carries a stored credential; a password here would be silently persisted.
    expect(
      validateCombined({ ...redshiftIamPayload(), secret: { password: 'super-secret' } }),
    ).toBe(false);
    // password auth without a password would produce an unusable connection.
    expect(validateCombined({ ...redshiftPasswordPayload(), secret: {} })).toBe(false);

    // Without the discriminator neither branch is selectable, whichever way it defaults.
    const passwordOptions: Record<string, unknown> = redshiftPasswordPayload().options;
    delete passwordOptions.authenticationType;
    const iamOptions: Record<string, unknown> = redshiftIamPayload().options;
    delete iamOptions.authenticationType;
    expect(
      validateCombined({ options: passwordOptions, secret: { password: 'super-secret' } }),
    ).toBe(false);
    expect(validateCombined({ options: iamOptions, secret: {} })).toBe(false);
  });

  it('SOURCE_REDSHIFT combinedSchema rejects an empty password', () => {
    const accountSchema = getAccountDefinitionSchema('redshift', 'SOURCE_REDSHIFT', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    // config-backend runs `combinedSchema` in place of `secretSchema`, so the non-empty
    // pattern declared there never executes. Without the same pattern here an account
    // stores an empty password, lib/pq drops it from the DSN, and the failure surfaces at
    // sync time rather than at create time.
    expect(validateCombined({ ...redshiftPasswordPayload(), secret: { password: '' } })).toBe(
      false,
    );
  });

  it('SOURCE_REDSHIFT db-config option and secret fields match its schema properties', async () => {
    const accountConfig = await getAccountDefinitionConfig(
      'redshift',
      'SOURCE_REDSHIFT',
      'sources',
    );
    const accountSchema = getAccountDefinitionSchema('redshift', 'SOURCE_REDSHIFT', 'sources');

    expect([...accountConfig.config.optionFields].sort()).toEqual(
      Object.keys(accountSchema.optionsSchema.properties).sort(),
    );
    expect([...accountConfig.config.secretFields].sort()).toEqual(
      Object.keys(accountSchema.secretSchema.properties).sort(),
    );
  });

  const databricksPatPayload = () => ({
    options: {
      host: 'dbc-abc12345-6789.cloud.databricks.com',
      port: 443,
      path: '/sql/1.0/warehouses/abcdef1234567890',
      catalog: 'main',
      authenticationType: 'pat',
    },
    secret: { token: 'dapi-super-secret' },
  });

  const databricksOauthPayload = () => ({
    options: {
      host: 'dbc-abc12345-6789.cloud.databricks.com',
      port: 443,
      path: '/sql/1.0/warehouses/abcdef1234567890',
      catalog: 'main',
      authenticationType: 'oauth',
      oauthClientId: 'client-id-123',
    },
    secret: { oauthClientSecret: 'client-secret-456' },
  });

  it('SOURCE_DATABRICKS account schema is valid against the account schema meta-schema', () => {
    const accountSchema = getAccountDefinitionSchema('databricks', 'SOURCE_DATABRICKS', 'sources');
    const metaSchema = JSON.parse(fs.readFileSync(accountSchemaMetaSchemaPath, 'utf-8'));
    const validateAccountSchema = compileAccountSchema(metaSchema);

    const isValid = validateAccountSchema(accountSchema);
    expect(validateAccountSchema.errors ?? []).toEqual([]);
    expect(isValid).toBe(true);
    expect(accountSchema.combinedSchema).toBeDefined();
  });

  it('SOURCE_DATABRICKS combinedSchema accepts the pat and oauth auth branches', () => {
    const accountSchema = getAccountDefinitionSchema('databricks', 'SOURCE_DATABRICKS', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(validateCombined(databricksPatPayload())).toBe(true);
    expect(validateCombined(databricksOauthPayload())).toBe(true);
  });

  it('SOURCE_DATABRICKS combinedSchema rejects credentials that do not match the auth branch', () => {
    const accountSchema = getAccountDefinitionSchema('databricks', 'SOURCE_DATABRICKS', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    // oauth must carry the client secret, never a personal access token.
    expect(
      validateCombined({ ...databricksOauthPayload(), secret: { token: 'dapi-super-secret' } }),
    ).toBe(false);
    // pat must carry the token, never an oauth client secret.
    expect(
      validateCombined({
        ...databricksPatPayload(),
        secret: { oauthClientSecret: 'client-secret-456' },
      }),
    ).toBe(false);

    // Without the discriminator neither branch is selectable, whichever way it defaults.
    const patOptions: Record<string, unknown> = databricksPatPayload().options;
    delete patOptions.authenticationType;
    const oauthOptions: Record<string, unknown> = databricksOauthPayload().options;
    delete oauthOptions.authenticationType;
    expect(validateCombined({ options: patOptions, secret: { token: 'dapi-super-secret' } })).toBe(
      false,
    );
    expect(
      validateCombined({
        options: oauthOptions,
        secret: { oauthClientSecret: 'client-secret-456' },
      }),
    ).toBe(false);
  });

  it('SOURCE_DATABRICKS combinedSchema rejects an empty token or client secret', () => {
    const accountSchema = getAccountDefinitionSchema('databricks', 'SOURCE_DATABRICKS', 'sources');
    const validateCombined = compileAccountSchema(accountSchema.combinedSchema);

    expect(validateCombined({ ...databricksPatPayload(), secret: { token: '' } })).toBe(false);
    expect(
      validateCombined({ ...databricksOauthPayload(), secret: { oauthClientSecret: '' } }),
    ).toBe(false);
  });

  it('SOURCE_DATABRICKS db-config option and secret fields match its schema properties', async () => {
    const accountConfig = await getAccountDefinitionConfig(
      'databricks',
      'SOURCE_DATABRICKS',
      'sources',
    );
    const accountSchema = getAccountDefinitionSchema('databricks', 'SOURCE_DATABRICKS', 'sources');

    expect([...accountConfig.config.optionFields].sort()).toEqual(
      Object.keys(accountSchema.optionsSchema.properties).sort(),
    );
    expect([...accountConfig.config.secretFields].sort()).toEqual(
      Object.keys(accountSchema.secretSchema.properties).sort(),
    );
  });

  const dataRetentionAccounts = getAccountNames('data-retention');
  dataRetentionAccounts.forEach((account) => {
    const [integration, accountName] = account.split('/');
    it(`${integration}/${accountName} - account definition test`, async () => {
      const accDefConfig = await getAccountDefinitionConfig(
        integration,
        accountName,
        'data-retention',
      );
      await expect(validateAccountDefinitions(accDefConfig)).resolves.toEqual(true);
    });
  });

  const malformedAccountDefConfigs = [
    {
      description: 'missing required properties',
      input: {
        config: {
          optionFields: ['region'],
        },
      },
      expected:
        '[" must have required property \'name\'"," must have required property \'type\'"," must have required property \'category\'"," must have required property \'authenticationType\'"]',
    },
    {
      description: 'invalid category',
      input: {
        name: 'INVALID_ACCOUNT',
        type: 'test',
        category: 'invalid_category',
        authenticationType: 'oauth',
        config: {
          optionFields: ['region'],
          refreshOAuthToken: true,
        },
      },
      expected: '["category must be equal to one of the allowed values"]',
    },
    {
      description: 'invalid authentication type',
      input: {
        name: 'INVALID_ACCOUNT',
        type: 'test',
        category: 'destination',
        authenticationType: 123,
        config: {
          optionFields: ['region'],
          refreshOAuthToken: true,
        },
      },
      expected: '["authenticationType must be string"]',
    },
    {
      description: 'invalid name format',
      input: {
        name: 'invalid-name',
        type: 'test',
        category: 'destination',
        authenticationType: 'oauth',
        config: {
          optionFields: ['region'],
          refreshOAuthToken: true,
        },
      },
      expected: '["name must match pattern \\"^[A-Z0-9_]+$\\""]',
    },
    {
      description: 'invalid optionFields',
      input: {
        name: 'INVALID_ACCOUNT',
        type: 'test',
        category: 'destination',
        authenticationType: 'oauth',
        config: {
          optionFields: [123],
          refreshOAuthToken: true,
        },
      },
      expected: '["config.optionFields.0 must be string"]',
    },
    {
      description: 'displayOptions wrong type',
      input: {
        name: 'INVALID_ACCOUNT',
        type: 'test',
        category: 'destination',
        authenticationType: 'oauth',
        config: {
          optionFields: ['region'],
          refreshOAuthToken: true,
        },
        displayOptions: 42,
      },
      expected: '["displayOptions must be object"]',
    },
    {
      description: 'displayOptions.deprecationLabel wrong type',
      input: {
        name: 'INVALID_ACCOUNT',
        type: 'test',
        category: 'destination',
        authenticationType: 'oauth',
        config: {
          optionFields: ['region'],
          refreshOAuthToken: true,
        },
        displayOptions: { deprecationLabel: 123 },
      },
      expected: '["displayOptions.deprecationLabel must be string"]',
    },
  ];

  it.each(malformedAccountDefConfigs)('$description', async (testCase) => {
    await expect(validateAccountDefinitions(testCase.input)).rejects.toThrow(
      new Error(testCase.expected),
    );
  });

  it('accepts boolean hidden', async () => {
    await expect(validateAccountDefinitions(getMinimalAccountDefinition(true))).resolves.toEqual(
      true,
    );
  });

  it('accepts hidden gate with a single flag and no condition', async () => {
    await expect(
      validateAccountDefinitions(
        getMinimalAccountDefinition({
          gate: {
            flags: [{ name: 'AMP_TEST_FLAG', value: false }],
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('accepts hidden gate with two flags and condition', async () => {
    await expect(
      validateAccountDefinitions(
        getMinimalAccountDefinition({
          gate: {
            flags: [
              { name: 'AMP_TEST_FLAG', value: false },
              { name: 'TEST_BILLING_FEATURE', value: false },
            ],
            condition: 'and',
          },
        }),
      ),
    ).resolves.toEqual(true);
  });

  it('rejects hidden gate with multiple flags and no condition', async () => {
    await expectValidationError(
      validateAccountDefinitions(
        getMinimalAccountDefinition({
          gate: {
            flags: [
              { name: 'AMP_TEST_FLAG', value: false },
              { name: 'TEST_BILLING_FEATURE', value: false },
            ],
          },
        }),
      ),
      "must have required property 'condition'",
      false,
    );
  });

  it('rejects legacy hidden feature flag object', async () => {
    await expectValidationError(
      validateAccountDefinitions(
        getMinimalAccountDefinition({
          featureFlagName: 'AMP_TEST_FLAG',
          featureFlagValue: false,
        }),
      ),
      "must have required property 'gate'",
      false,
    );
  });
});

type ClickHouseFieldCase = {
  id: string;
  field: 'host' | 'name' | 'password';
  input: string;
  verdict: 'pass' | 'fail';
  error?: string;
  configBackendVerdict?: 'pass' | 'fail';
  configBackendErrorPrefix?: string;
};

const CLICKHOUSE_ERROR_TEXT = {
  host: 'Enter a hostname or a dotted-decimal IPv4 address without a scheme, port or path.',
  name: 'Use letters, digits and underscores, start with a letter or underscore, at most 128 characters.',
  password: 'The password cannot contain control characters or start or end with whitespace.',
};

function clickHouseFieldCases(): ClickHouseFieldCase[] {
  return JSON.parse(
    fs.readFileSync(
      path.resolve(__dirname, './data/validation/accounts/clickhouse-fields.json'),
      'utf-8',
    ),
  ).cases;
}

// Other repositories copy these files byte for byte, and the LLD requires `\u` escapes above U+00FF.
// An editor that turns an escape into the literal character changes the bytes the copies compare.
function expectAsciiOnly(relativePath: string): void {
  const bytes = fs.readFileSync(path.resolve(__dirname, '..', relativePath));
  expect({ file: relativePath, firstNonAscii: bytes.findIndex((b) => b > 127) }).toEqual({
    file: relativePath,
    firstNonAscii: -1,
  });
}

describe('ClickHouse shared field fixtures', () => {
  it('the fixture file is pure ASCII', () => {
    expectAsciiOnly('test/data/validation/accounts/clickhouse-fields.json');
  });

  const inputsOf = (field: ClickHouseFieldCase['field'], verdict: 'pass' | 'fail') =>
    clickHouseFieldCases()
      .filter((c) => c.field === field && c.verdict === verdict)
      .map((c) => c.input);

  it('every fixture case has a unique id, a known field, a verdict and its rule error text', () => {
    const cases = clickHouseFieldCases();
    const ids = cases.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
    cases.forEach((c) => {
      expect(['host', 'name', 'password']).toContain(c.field);
      expect(typeof c.input).toBe('string');
      expect(['pass', 'fail']).toContain(c.verdict);
      if (c.verdict === 'fail') {
        expect({ id: c.id, error: c.error }).toEqual({
          id: c.id,
          error: CLICKHOUSE_ERROR_TEXT[c.field],
        });
      } else {
        expect({ id: c.id, error: c.error }).toEqual({ id: c.id, error: undefined });
      }
      if (c.configBackendVerdict !== undefined) {
        expect({
          id: c.id,
          field: c.field,
          verdict: c.configBackendVerdict,
          prefix: c.configBackendErrorPrefix,
        }).toEqual({
          id: c.id,
          field: 'password',
          verdict: 'fail',
          prefix: 'Configuration contains syntax errors',
        });
      }
    });
  });

  // A deleted case would silently drop its check in every copy, so pin the exact id set.
  it('the fixture holds exactly the 65 spec cases, and P40 to P42 carry the config-backend refusal', () => {
    const idRange = (prefix: string, from: number, to: number) =>
      Array.from(
        { length: to - from + 1 },
        (_, i) => `${prefix}${String(from + i).padStart(2, '0')}`,
      );
    const cases = clickHouseFieldCases();
    expect(cases.map((c) => c.id)).toEqual([
      ...idRange('H', 1, 8),
      ...idRange('H', 20, 34),
      ...idRange('N', 1, 5),
      ...idRange('N', 20, 27),
      ...idRange('P', 1, 9),
      ...idRange('P', 20, 36),
      ...idRange('P', 40, 42),
    ]);
    expect(cases.filter((c) => c.configBackendVerdict !== undefined).map((c) => c.id)).toEqual([
      'P40',
      'P41',
      'P42',
    ]);
  });

  it('the fixture keeps every host and name input the spec names', () => {
    expect(inputsOf('host', 'pass')).toEqual(
      expect.arrayContaining(['127.0.0.1', '10.0.0.5', 'ch.example.com', '1password.com']),
    );
    expect(inputsOf('host', 'fail')).toEqual(
      expect.arrayContaining([
        '1.2.3',
        '0x7f000001',
        '010.0.0.1',
        '256.1.1.1',
        '::1',
        'https://ch.example.com',
        'ch.example.com:8443',
      ]),
    );
    expect(inputsOf('name', 'pass')).toEqual(
      expect.arrayContaining(['analytics', '_scratch', 'Mixed_Case_1', '_rudderstack_ws1']),
    );
    expect(inputsOf('name', 'fail')).toEqual(
      expect.arrayContaining([
        'my-db',
        'analytics.v2',
        '1db',
        'analyst@example.com',
        'a`b',
        'a b',
        '',
        'a'.repeat(129),
      ]),
    );
  });

  it('the fixture keeps every password parity input of catalog LLD section 3.8', () => {
    expect(inputsOf('password', 'pass')).toEqual(
      expect.arrayContaining([
        'p w',
        'p\u00A0w',
        'p\u00E4ssw\u00F6rd',
        'p\u{1F600}w',
        'ab{{cd',
        '{{}}',
        'env.',
      ]),
    );
    expect(inputsOf('password', 'fail')).toEqual(
      expect.arrayContaining([
        '\u00A0pw',
        'pw\u00A0',
        '\u2003pw',
        'pw\u3000',
        '\uFEFFpw',
        ' pw',
        'pw ',
        'p\u0085w',
        'p\u009Fw',
        'p\tw',
        'p\u0000w',
        'p\u007Fw',
      ]),
    );
  });
});

const CLICKHOUSE_GATE = {
  gate: { flags: [{ name: 'AMP_enable-clickhouse-retl-source', value: false }] },
};

// A bare boolean never consults a flag, and config-backend refuses every workspace with `true`.
function expectClickHouseGate(hidden: unknown): void {
  expect(hidden).toEqual(CLICKHOUSE_GATE);
}

describe('SOURCE_CLICKHOUSE account definition', () => {
  const loadAccount = () =>
    getAccountDefinitionConfig('clickhouse', 'SOURCE_CLICKHOUSE', 'sources');

  it('declares a password source account of type clickhouse that passes the account meta-schema', async () => {
    const accountConfig = await loadAccount();
    await expect(validateAccountDefinitions(accountConfig)).resolves.toEqual(true);
    expect(accountConfig).toMatchObject({
      name: 'SOURCE_CLICKHOUSE',
      type: 'clickhouse',
      category: 'source',
      authenticationType: 'password',
    });
  });

  it('has exactly six options and the one secret password, with no CA or transport option', async () => {
    const accountConfig = await loadAccount();
    expect(accountConfig.config.optionFields).toEqual([
      'host',
      'port',
      'database',
      'user',
      'secure',
      'skipVerify',
    ]);
    expect(accountConfig.config.secretFields).toEqual(['password']);
    ['caCertificate', 'protocol', 'nativePort', 'authenticationType'].forEach((field) => {
      expect(accountConfig.config.optionFields).not.toContain(field);
    });
  });

  it('displayOptions.hidden is the creation gate object', async () => {
    const accountConfig = await loadAccount();
    expectClickHouseGate(accountConfig.displayOptions.hidden);
  });

  it('the account meta-schema refuses a legacy feature-flag hidden', async () => {
    const legacy = {
      featureFlagName: 'AMP_enable-clickhouse-retl-source',
      featureFlagValue: false,
    };
    const accountConfig = await loadAccount();
    await expectValidationError(
      validateAccountDefinitions({ ...accountConfig, displayOptions: { hidden: legacy } }),
      "must have required property 'gate'",
      false,
    );
  });
});

const clickHouseOptions = (): Record<string, unknown> => ({
  host: 'ch.example.com',
  port: 8443,
  database: 'analytics',
  user: 'rudder',
  secure: true,
  skipVerify: false,
});

const clickHouseAccountSchema = () =>
  getAccountDefinitionSchema('clickhouse', 'SOURCE_CLICKHOUSE', 'sources');

// Lookaround, \s and \p{} read differently in ECMA-262 and Go RE2 (catalog LLD section 3.3). This is a
// syntax check only: sqlconnect-go runs the shared fixture cases through Go RE2.
const RE2_UNSAFE_PATTERN = /\(\?[=!<]|\\s|\\p\{/;

describe('SOURCE_CLICKHOUSE optionsSchema', () => {
  const validateOptions = () => compileAccountSchema(clickHouseAccountSchema().optionsSchema);
  const validateWithText = () =>
    compileAccountSchemaWithErrorMessages(clickHouseAccountSchema().optionsSchema);
  const messages = (validate: ValidateFunction) => (validate.errors ?? []).map((e) => e.message);

  it('the account schema is valid against the account meta-schema and has no combinedSchema', () => {
    const metaSchema = JSON.parse(
      fs.readFileSync(path.resolve('src/schemas/account/account-schema-schema.json'), 'utf-8'),
    );
    const validateAccountSchema = compileAccountSchema(metaSchema);
    const accountSchema = clickHouseAccountSchema();
    const isValid = validateAccountSchema(accountSchema);
    expect(validateAccountSchema.errors ?? []).toEqual([]);
    expect(isValid).toBe(true);
    expect(accountSchema.combinedSchema).toBeUndefined();
    expect(accountSchema.optionsSchema.additionalProperties).toBeUndefined();
  });

  it('optionFields equal the optionsSchema property names', async () => {
    const accountConfig = await getAccountDefinitionConfig(
      'clickhouse',
      'SOURCE_CLICKHOUSE',
      'sources',
    );
    expect([...accountConfig.config.optionFields].sort()).toEqual(
      Object.keys(clickHouseAccountSchema().optionsSchema.properties).sort(),
    );
  });

  it('a complete option set passes and omitted port, secure and skipVerify take their defaults', () => {
    const validate = validateOptions();
    expect(validate(clickHouseOptions())).toBe(true);
    const options = clickHouseOptions();
    delete options.port;
    delete options.secure;
    delete options.skipVerify;
    expect(validate(options)).toBe(true);
    expect(options).toMatchObject({ port: 8443, secure: true, skipVerify: false });
  });

  it('port accepts 1, 8123, 8443 and 65535 and rejects 0, 65536, "8443", 1.5 and -1 without coercion', () => {
    const validate = validateOptions();
    [1, 8123, 8443, 65535].forEach((port) => {
      expect({ port, valid: validate({ ...clickHouseOptions(), port }) }).toEqual({
        port,
        valid: true,
      });
    });
    [0, 65536, '8443', 1.5, -1].forEach((port) => {
      const options = { ...clickHouseOptions(), port };
      expect({ port, valid: validate(options) }).toEqual({ port, valid: false });
      expect(options.port).toBe(port);
    });
  });

  it('null option values fail and are not defaulted', () => {
    const validate = validateOptions();
    ['port', 'secure', 'skipVerify'].forEach((key) => {
      const options = { ...clickHouseOptions(), [key]: null };
      expect({ key, valid: validate(options) }).toEqual({ key, valid: false });
      expect(options[key]).toBeNull();
    });
  });

  it('each missing required option fails with the AJV required message', () => {
    const validate = validateWithText();
    ['host', 'database', 'user'].forEach((key) => {
      const options = clickHouseOptions();
      delete options[key];
      expect(validate(options)).toBe(false);
      expect(messages(validate)).toEqual([`must have required property '${key}'`]);
    });
  });

  it('secure is const true and skipVerify is const false; non-boolean TLS values fail', () => {
    const validate = validateOptions();
    const schema = clickHouseAccountSchema().optionsSchema;
    expect(schema.required).not.toContain('secure');
    expect(schema.properties.secure).toEqual({ type: 'boolean', const: true, default: true });
    expect(schema.properties.skipVerify).toEqual({ type: 'boolean', const: false, default: false });
    expect(validate({ ...clickHouseOptions(), secure: false })).toBe(false);
    expect(validate({ ...clickHouseOptions(), skipVerify: true })).toBe(false);
    ['secure', 'skipVerify'].forEach((key) => {
      ['true', 'false', 0, 1].forEach((value) => {
        expect({ key, value, valid: validate({ ...clickHouseOptions(), [key]: value }) }).toEqual({
          key,
          value,
          valid: false,
        });
      });
    });
  });

  it('host cases from the shared fixture file', () => {
    const validate = validateWithText();
    clickHouseFieldCases()
      .filter((c) => c.field === 'host')
      .forEach((c) => {
        const valid = validate({ ...clickHouseOptions(), host: c.input });
        expect({ id: c.id, verdict: valid ? 'pass' : 'fail' }).toEqual({
          id: c.id,
          verdict: c.verdict,
        });
        if (!valid)
          expect({ id: c.id, messages: messages(validate) }).toEqual({
            id: c.id,
            messages: [c.error],
          });
      });
  });

  it('name cases apply to database and user with one error text', () => {
    const validate = validateWithText();
    clickHouseFieldCases()
      .filter((c) => c.field === 'name')
      .forEach((c) => {
        ['database', 'user'].forEach((key) => {
          const valid = validate({ ...clickHouseOptions(), [key]: c.input });
          expect({ id: c.id, key, verdict: valid ? 'pass' : 'fail' }).toEqual({
            id: c.id,
            key,
            verdict: c.verdict,
          });
          if (!valid) {
            expect({ id: c.id, key, messages: messages(validate) }).toEqual({
              id: c.id,
              key,
              messages: [c.error],
            });
          }
        });
      });
  });

  it('requires only host, database and user, without a working database option', () => {
    const schema = clickHouseAccountSchema().optionsSchema;
    expect(schema.required).toEqual(['host', 'database', 'user']);
    expect(Object.keys(schema.properties)).toEqual([
      'host',
      'port',
      'database',
      'user',
      'secure',
      'skipVerify',
    ]);
    const validate = validateOptions();
    const options = clickHouseOptions();
    expect(validate(options)).toBe(true);
    expect(options).not.toHaveProperty('rudderSchema');
  });

  it('accepts and preserves a rudderSchema credential override without declaring a form option', () => {
    const validate = validateOptions();
    const options = { ...clickHouseOptions(), rudderSchema: 'custom_rudder' };
    expect(validate(options)).toBe(true);
    expect(options.rudderSchema).toBe('custom_rudder');
    expect(clickHouseAccountSchema().optionsSchema.properties.rudderSchema).toBeUndefined();
  });

  it('the options schema accepts and keeps undeclared options; the config-backend guard refuses them', () => {
    const validate = validateOptions();
    const options = {
      ...clickHouseOptions(),
      protocol: 'http',
      nativePort: 9440,
      caCertificate: 'x',
    };
    expect(validate(options)).toBe(true);
    expect(options).toMatchObject({ protocol: 'http', nativePort: 9440, caCertificate: 'x' });
  });

  it('option patterns use no lookaround, \\s or \\p{}, and host keeps maxLength 253', () => {
    const { properties } = clickHouseAccountSchema().optionsSchema;
    ['host', 'database', 'user'].forEach((key) => {
      expect({ key, unsafe: RE2_UNSAFE_PATTERN.test(properties[key].pattern) }).toEqual({
        key,
        unsafe: false,
      });
    });
    expect(properties.host.maxLength).toBe(253);
    expect(properties.database.pattern).toBe('^[A-Za-z_][A-Za-z0-9_]{0,127}$');
    expect(properties.user.pattern).toBe(properties.database.pattern);
  });
});

describe('SOURCE_CLICKHOUSE secretSchema', () => {
  const validateSecret = () =>
    compileAccountSchemaWithErrorMessages(clickHouseAccountSchema().secretSchema);

  it('secretFields equal the secretSchema property names', async () => {
    const accountConfig = await getAccountDefinitionConfig(
      'clickhouse',
      'SOURCE_CLICKHOUSE',
      'sources',
    );
    expect(accountConfig.config.secretFields).toEqual(
      Object.keys(clickHouseAccountSchema().secretSchema.properties),
    );
  });

  it('password cases from the shared fixture file', () => {
    const validate = validateSecret();
    clickHouseFieldCases()
      .filter((c) => c.field === 'password')
      .forEach((c) => {
        const valid = validate({ password: c.input });
        expect({ id: c.id, verdict: valid ? 'pass' : 'fail' }).toEqual({
          id: c.id,
          verdict: c.verdict,
        });
        if (!valid) {
          expect({ id: c.id, messages: (validate.errors ?? []).map((e) => e.message) }).toEqual({
            id: c.id,
            messages: [c.error],
          });
        }
      });
  });

  it('an absent, empty or non-string password fails', () => {
    const validate = validateSecret();
    expect(validate({})).toBe(false);
    expect((validate.errors ?? []).map((e) => e.message)).toEqual([
      "must have required property 'password'",
    ]);
    [{ password: '' }, { password: 5 }, { password: null }].forEach((secret) => {
      expect({ secret, valid: validate(secret) }).toEqual({ secret, valid: false });
    });
  });

  it('the password is never trimmed by validation', () => {
    const validate = validateSecret();
    const secret = { password: 'p w' };
    expect(validate(secret)).toBe(true);
    expect(secret.password).toBe('p w');
  });

  it('the secret schema accepts and keeps an undeclared secret; the config-backend guard refuses it', () => {
    const validate = validateSecret();
    const secret = { password: 'secret', unexpected: 1 };
    expect(validate(secret)).toBe(true);
    expect(secret.unexpected).toBe(1);
    expect(clickHouseAccountSchema().secretSchema.additionalProperties).toBeUndefined();
  });

  it('schema.json is pure ASCII, so the password escapes survive', () => {
    expectAsciiOnly('src/configurations/sources/clickhouse/accounts/SOURCE_CLICKHOUSE/schema.json');
  });

  it('the password pattern uses no lookaround, \\s or \\p{}', () => {
    expect(
      RE2_UNSAFE_PATTERN.test(clickHouseAccountSchema().secretSchema.properties.password.pattern),
    ).toBe(false);
  });
});

describe('clickhouse source definition', () => {
  const loadSource = async () => (await getSourceDefinitionConfig('clickhouse')).default;

  it('links SOURCE_CLICKHOUSE and declares mirror as the only sync behaviour', async () => {
    const srcDefConfig = await loadSource();
    await expect(validateSourceDefinitions(srcDefConfig)).resolves.toEqual(true);
    expect(srcDefConfig).toMatchObject({
      name: 'clickhouse',
      category: 'warehouse',
      type: 'warehouse',
      displayName: 'ClickHouse',
    });
    expect(srcDefConfig.config.supportedAccountDefinitions.rudderAccountId).toEqual([
      'SOURCE_CLICKHOUSE',
    ]);
    expect(srcDefConfig.options).toMatchObject({
      syncBehaviours: ['mirror'],
      supportsSyncSettings: true,
      isCredentialsValidationSupported: true,
      isSqlModelSupported: false,
      isAudienceSupported: false,
      isDataGraphSupported: false,
      icon: 'clickhouse',
    });
  });

  it('options.hidden is the creation gate object', async () => {
    expectClickHouseGate((await loadSource()).options.hidden);
  });

  it('validateSourceDefinitions refuses a legacy feature-flag hidden on clickhouse', async () => {
    const srcDefConfig = await loadSource();
    await expectValidationError(
      validateSourceDefinitions({
        ...srcDefConfig,
        options: {
          ...srcDefConfig.options,
          hidden: { featureFlagName: 'AMP_enable-clickhouse-retl-source', featureFlagValue: false },
        },
      }),
      "must have required property 'gate'",
      false,
    );
  });
});

describe('clickhouse source compatibility fixtures', () => {
  it('the fixture file holds the eleven catalog entries plus the nested config refusal, and every refusal carries an err array', () => {
    const entries = getIntegrationData('clickhouse', 'sources');
    expect(entries.map((e) => e.testTitle)).toEqual([
      'Account reference only',
      'Account reference with non-secret connection fields',
      'Inline config with password',
      'Inline config without password',
      'Inline config with empty password',
      'Account reference with password',
      'Account reference with empty password',
      'Empty account reference',
      'Account reference of 101 characters',
      'Numeric account reference',
      'Account reference with an extra non-secret field',
      'Account reference with a nested config object',
    ]);
    entries
      .filter((e) => e.result === false)
      .forEach((e) =>
        expect({ title: e.testTitle, hasErr: Array.isArray(e.err) }).toEqual({
          title: e.testTitle,
          hasErr: true,
        }),
      );
  });
});

describe('clickhouse ui-config', () => {
  const PORT_REGEX =
    '^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$';
  const loadUiConfig = () =>
    JSON.parse(
      fs.readFileSync(
        path.resolve('src/configurations/sources/clickhouse/ui-config.json'),
        'utf-8',
      ),
    ).uiConfig[0];
  const field = (value: string) =>
    loadUiConfig().fields.find((f: { value: string }) => f.value === value);

  it('ui-config.json is pure ASCII, so the password regex escapes survive', () => {
    expectAsciiOnly('src/configurations/sources/clickhouse/ui-config.json');
  });

  it('renders the five account inputs in order and no working database, TLS, dbname or CA input', () => {
    expect(loadUiConfig().fields.map((f: { value: string }) => f.value)).toEqual([
      'host',
      'port',
      'database',
      'user',
      'password',
    ]);
  });

  it('ui-config string field regexes equal the account schema patterns', () => {
    const { optionsSchema, secretSchema } = clickHouseAccountSchema();
    ['host', 'database', 'user'].forEach((key) => {
      expect({ key, regex: field(key).regex }).toEqual({
        key,
        regex: optionsSchema.properties[key].pattern,
      });
    });
    expect(field('password').regex).toBe(secretSchema.properties.password.pattern);
  });

  it('ui-config port regex accepts 1 to 65535 only', () => {
    expect(field('port').regex).toBe(PORT_REGEX);
    const port = new RegExp(field('port').regex);
    [
      '1',
      '443',
      '8123',
      '8443',
      '9999',
      '10000',
      '59999',
      '64999',
      '65499',
      '65529',
      '65535',
    ].forEach((v) => expect({ v, ok: port.test(v) }).toEqual({ v, ok: true }));
    ['', '0', '00001', '65536', '70000', '99999', '8443a', '-1', '1.5'].forEach((v) =>
      expect({ v, ok: port.test(v) }).toEqual({ v, ok: false }),
    );
    // A number, not a string: TextInputField sends `field.default` unchanged on mount (textInput.tsx:84),
    // and the account schema port is an integer.
    expect(field('port')).toMatchObject({
      inputFieldType: 'number',
      required: true,
      default: 8443,
    });
    expect(field('port').regexErrorMessage).toBe('Enter an integer from 1 to 65535');
  });

  // Catalog LLD section 3.5: the form shows a short text; the account schema errorMessage has the full rule.
  it('the host regexErrorMessage is under eight words with no final full stop', () => {
    const message: string = field('host').regexErrorMessage;
    expect(message.split(' ').length).toBeLessThan(8);
    expect(message.endsWith('.')).toBe(false);
  });

  it('the name field hint states the leading-digit rule the regex enforces', () => {
    ['database', 'user'].forEach((key) => {
      expect({ key, refused: !new RegExp(field(key).regex).test('2024_events') }).toEqual({
        key,
        refused: true,
      });
      expect({ key, message: field(key).regexErrorMessage }).toEqual({
        key,
        message: 'Letters, digits, underscores; no leading digit',
      });
    });
  });

  it('every regex has a regexErrorMessage, and required flags match the account schema', () => {
    const { optionsSchema, secretSchema } = clickHouseAccountSchema();
    const requiredFields = new Set([...optionsSchema.required, ...secretSchema.required]);
    // The form sends its port default on mount; an API client may omit port and use the schema default.
    expect(optionsSchema.required).not.toContain('port');
    expect(optionsSchema.properties.port.default).toBe(8443);
    expect(field('port')).toMatchObject({ required: true, default: 8443 });
    expect([...requiredFields].sort()).toEqual(
      loadUiConfig()
        .fields.filter(
          (f: { value: string; required?: boolean }) => f.required && f.value !== 'port',
        )
        .map((f: { value: string }) => f.value)
        .sort(),
    );
    loadUiConfig().fields.forEach(
      (f: { value: string; regex?: string; regexErrorMessage?: string; required?: boolean }) => {
        expect({ value: f.value, hasMessage: typeof f.regexErrorMessage === 'string' }).toEqual({
          value: f.value,
          hasMessage: true,
        });
        expect({ value: f.value, required: f.required }).toEqual({
          value: f.value,
          required: requiredFields.has(f.value) || f.value === 'port',
        });
      },
    );
  });

  it('keeps the account summary, secret and doc link contract', () => {
    const ui = loadUiConfig();
    expect(ui.schemaAlias).toBe('Database');
    expect(ui.nameField).toBe('user');
    expect(ui.secretFields).toEqual(['password']);
    expect(field('password')).toMatchObject({ secret: true, inputFieldType: 'password' });
    expect(field('password').trim).toBeUndefined();
    expect(Object.keys(ui.docLinks).sort()).toEqual([
      'grantPermissions',
      'jsonMapperUseInstructions',
      'setupInstructions',
      'verifyingCredentials',
    ]);
    expect(ui.docLinks.setupInstructions).toBe(
      'https://docs.rudderstack.com/reverse-etl/clickhouse',
    );
    expect(ui.docLinks.jsonMapperUseInstructions).toBe(
      'https://docs.rudderstack.com/reverse-etl/clickhouse/#specifying-the-data-to-import',
    );
  });
});
