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

async function getSourceDefinitionConfig(srcName: string) {
  const dirPath = path.resolve(`src/configurations/sources/${srcName}`);
  const configPath = `${dirPath}/db-config.json`;
  return import(configPath);
}

async function getDestinationDefinitionConfig(destName: string) {
  const dirPath = path.resolve(`src/configurations/destinations/${destName}`);
  const configPath = `${dirPath}/db-config.json`;
  return import(configPath);
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
      description: 'hybridModeCloudEventsFilter is not a valid map',
      input: {
        name: 'test',
        displayName: 'Test',
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
  ];

  it.each(malformedDestDefConfigs)('$description', async (testCase) => {
    await expect(validateDestinationDefinitions(testCase.input)).rejects.toThrow(
      new Error(testCase.expected),
    );
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
  ];

  it.each(malformedSrcDefConfigs)('$description', async (testCase) => {
    await expect(validateSourceDefinitions(testCase.input)).rejects.toThrow(
      new Error(testCase.expected),
    );
  });
});
