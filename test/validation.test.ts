/* eslint-disable no-console */
/* eslint-disable max-len */
import fs from 'fs';
import path from 'path';
import Commander from 'commander';
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

function findFieldByConfigKey(
  node: unknown,
  configKey: string,
): Record<string, unknown> | undefined {
  if (Array.isArray(node)) {
    return node.reduce<Record<string, unknown> | undefined>(
      (result, item) => result || findFieldByConfigKey(item, configKey),
      undefined,
    );
  }

  if (node && typeof node === 'object') {
    const record = node as Record<string, unknown>;
    if (record.configKey === configKey) return record;

    return Object.values(record).reduce<Record<string, unknown> | undefined>(
      (result, value) => result || findFieldByConfigKey(value, configKey),
      undefined,
    );
  }

  return undefined;
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

  describe('Braze UI field visibility', () => {
    it('shows ecommerce recommended events only for cloud-mode connections', () => {
      const brazeUiConfig = JSON.parse(
        fs.readFileSync(
          path.resolve('src/configurations/destinations/braze/ui-config.json'),
          'utf-8',
        ),
      );
      const field = findFieldByConfigKey(brazeUiConfig, 'useEcommerceRecommendedEvents');
      expect(field).toBeDefined();
      expect(field?.default).toBeUndefined();

      const preRequisites = field?.preRequisites as Record<string, unknown>;
      const fields = preRequisites.fields as Record<string, unknown>[];
      expect(fields).toEqual([
        { configKey: 'connectionMode.cloud', value: 'cloud' },
        { configKey: 'connectionMode.web', value: 'cloud' },
        { configKey: 'connectionMode.android', value: 'cloud' },
        { configKey: 'connectionMode.androidKotlin', value: 'cloud' },
        { configKey: 'connectionMode.ios', value: 'cloud' },
        { configKey: 'connectionMode.iosSwift', value: 'cloud' },
        { configKey: 'connectionMode.flutter', value: 'cloud' },
        { configKey: 'connectionMode.reactnative', value: 'cloud' },
        { configKey: 'connectionMode.unity', value: 'cloud' },
        { configKey: 'connectionMode.amp', value: 'cloud' },
        { configKey: 'connectionMode.cordova', value: 'cloud' },
        { configKey: 'connectionMode.shopify', value: 'cloud' },
        { configKey: 'connectionMode.warehouse', value: 'cloud' },
      ]);
      expect(preRequisites.condition).toBe('or');

      const brazeDbConfig = JSON.parse(
        fs.readFileSync(
          path.resolve('src/configurations/destinations/braze/db-config.json'),
          'utf-8',
        ),
      );
      expect(brazeDbConfig.config.destConfig.defaultConfig).not.toContain(
        'useEcommerceRecommendedEvents',
      );
    });
  });

  describe('Warehouse sync frequency validation', () => {
    const warehouseDestinationNames = [
      'azure_datalake',
      'azure_synapse',
      'bq',
      'clickhouse',
      'deltalake',
      'gcs_datalake',
      'mssql',
      'postgres',
      'rs',
      's3_datalake',
      'snowflake',
    ];

    warehouseDestinationNames.forEach((dest) => {
      it(`${dest} accepts 10-minute sync frequency and rejects invalid frequency`, () => {
        const validCase = getIntegrationData(dest, 'destinations')?.find(
          (td) => td.result === true,
        );
        if (!validCase) {
          throw new Error(`Missing valid test fixture for warehouse destination: ${dest}`);
        }

        const baseConfig = validCase.config as Record<string, unknown>;
        expect(() => {
          validateConfig(dest, { ...baseConfig, syncFrequency: '10' }, 'destinations', true);
        }).not.toThrow();
        expect(() => {
          validateConfig(dest, { ...baseConfig, syncFrequency: '11' }, 'destinations', true);
        }).toThrow();
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
