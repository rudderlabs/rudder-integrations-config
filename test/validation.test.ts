/* eslint-disable no-console */
/* eslint-disable max-len */
import fs from 'fs';
import path from 'path';
import Commander from 'commander';
import {
  init,
  validateConfig,
  validateSourceDefinitions,
  validateSourceType,
  validateDestinationDefinitions,
  validateHybridModeCloudConfig,
} from '../src';

const command = new Commander.Command();
command
  .allowUnknownOption()
  .option('-d, --destinations <string>', 'Enter destination names separated by comma', 'all')
  .option('-s, --sources <string>', 'Enter source names separated by comma', 'all')
  .parse();

const cmdOpts = command.opts();

function getIntegrationNames(type) {
  const dirPath = path.resolve(`src/configurations/${type}`);
  return fs.readdirSync(dirPath).filter((file) => fs.statSync(`${dirPath}/${file}`).isDirectory());
}

function getIntegrationData(name, type): Record<string, unknown>[] {
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
        it(`TC ${tcIdx + 1}`, () => {
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
        it(`TC ${tcIdx + 1}`, () => {
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
          destConfig: {},
        },
      },
      expected:
        '[" must have required property \'name\'"," must have required property \'displayName\'"]',
    },
  ];

  it.each(malformedDestDefConfigs)('$description', async (testCase) => {
    await expect(validateDestinationDefinitions(testCase.input)).rejects.toThrow(
      new Error(testCase.expected),
    );
  });
});

describe('Destination Definition wrong hybrid mode configuration tests', () => {
  const supportedSourceTypes = ['web', 'android', 'amp', 'cloud', 'flutter'];
  const destinationDefinition = {
    config: {
      supportedSourceTypes,
      hybridModeCloudEventsFilter: {},
    },
  };
  const testCases = [
    {
      caseName:
        'should return false, when destinationDefinition.config.hybridModeCloudEventsFilter is not a valid map',
      hybridModeCloudEventsFilter: [],
      expected: false,
    },
    {
      caseName:
        'should return false, when destinationDefinition.config.hybridModeCloudEventsFilter is empty map',
      hybridModeCloudEventsFilter: {},
      expected: false,
    },
    {
      caseName:
        'should return false, when destinationDefinition.config.hybridModeCloudEventsFilter has sourceType that is not present in supportedSourceTypes',
      hybridModeCloudEventsFilter: {
        web: {
          messageType: ['track'],
        },
        differentSourceType: {
          messageType: ['page', 'group'],
        },
      },
      expected: false,
    },
    {
      caseName:
        'should return false, destinationDefinition.config.hybridModeCloudEventsFilter[web] = {}',
      hybridModeCloudEventsFilter: {
        web: {},
      },
      expected: false,
    },
    {
      caseName:
        'should return false, when destinationDefinition.config.hybridModeCloudEventsFilter[web] = { randomType: ["random_1", "random_2"] }',
      hybridModeCloudEventsFilter: {
        web: {
          randomType: ['random_1', 'random_2'],
        },
      },
      expected: false,
    },
    {
      caseName:
        'should return false, when destinationDefinition.config.hybridModeCloudEventsFilter[web] = { messageType: "track" }',
      hybridModeCloudEventsFilter: {
        web: {
          messageType: 'track',
        },
      },
      expected: false,
    },
  ];

  it.each(testCases)('$caseName', (testCase) => {
    destinationDefinition.config.hybridModeCloudEventsFilter = testCase.hybridModeCloudEventsFilter;
    const isValid = validateHybridModeCloudConfig(destinationDefinition);
    expect(isValid).toBe(testCase.expected);
  });

  it('should return true, when destinationDefinition is undefined', () => {
    expect(validateHybridModeCloudConfig(undefined)).toEqual(true);
  });
  it('should return true, when destinationDefinition.config is undefined', () => {
    expect(validateHybridModeCloudConfig({ config: undefined })).toEqual(true);
  });
  it('should return true, when destinationDefinition.config.supportedSourceTypes is undefined', () => {
    expect(validateHybridModeCloudConfig({ config: { supportedSourceTypes: undefined } })).toEqual(
      true,
    );
  });
  it('should return true, when destinationDefinition.config.hybridModeCloudEventsFilter is undefined', () => {
    expect(
      validateHybridModeCloudConfig({
        config: { supportedSourceTypes, hybridModeCloudEventsFilter: undefined },
      }),
    ).toEqual(true);
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
