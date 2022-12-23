/* eslint-disable max-len */
import { init, validateConfig } from '../src';
import fs from 'fs';
import path from 'path';
import Commander from 'commander';

const command = new Commander.Command();
command
  .allowUnknownOption()
  .option('-d, --destinations <string>', 'Enter destination names separated by comma', 'all')
  .option('-s, --sources <string>', 'Enter source names separated by comma', 'all')
  .parse();

const cmdOpts = command.opts();

function getIntegrationNames(type) {
  const dirPath = path.resolve(`src/configurations/${type}`);
  return fs.readdirSync(dirPath).filter(function (file) {
    return fs.statSync(dirPath + '/' + file).isDirectory();
  });
}

function getIntegrationData(name, type) {
  try {
    return JSON.parse(
      fs.readFileSync(path.resolve(__dirname, `./data/validation/${type}/${name}.json`), 'utf-8'),
    );
  } catch (e) {
    // console.error(e);
    // console.error(`Unable to load test data for: "${name}" (${type})`);
  }
}

let destList: string[] = [];
if (cmdOpts.destinations !== 'all') {
  destList = cmdOpts.destinations
    .split(',')
    .map((x: string) => x.trim())
    .filter((x: any) => x);
  console.log(`Destinations specified: ${destList}`);
} else {
  destList = getIntegrationNames('destinations');
}
const destTcData = {};
destList.forEach((d) => {
  const intgData = getIntegrationData(d, 'destinations');
  if (intgData) destTcData[d] = intgData;
});

let srcList: string[] = [];
if (cmdOpts.sources !== 'all') {
  srcList = cmdOpts.sources
    .split(',')
    .map((x: string) => x.trim())
    .filter((x: any) => x);
  console.log(`Sources specified: ${srcList}`);
} else {
  srcList = getIntegrationNames('sources');
}
const srcTcData = {};
srcList.forEach((s) => {
  const intgData = getIntegrationData(s, 'sources');
  if (intgData) srcTcData[s] = intgData;
});

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

describe('Core Tests', () => {
  it('If invalid integration name is provide, throw error', async () => {
    expect(() => {
      validateConfig('', {}, "destinations", true);
    }).toThrow('Missing definitionName');
  });

  it('If unknown integration name is provided, throw error', async () => {
    init();
    await delay(1000);

    const invalidIntg = 'INVALID_INTEGRATION_NAME';
    expect(() => {
      validateConfig(invalidIntg, {}, "destinations", true);
    }).toThrow(`No validation method found for definition ${invalidIntg}`);
  });

  it('If unknown integration name is provided and throw errors flag is disabled, no error should be thrown', async () => {
    init();
    await delay(1000);

    const invalidIntg = 'INVALID_INTEGRATION_NAME';
    expect(() => {
      validateConfig(invalidIntg, {}, "destinations");
    }).not.toThrow();
  });
});

describe('Validation Tests', () => {
  beforeAll(async () => {
    init();
    await delay(1000);
  });

  // Destination tests
  Object.keys(destTcData).forEach((dest: any, destIdx: number) => {
    describe(`${destIdx + 1}. Destination - ${dest}`, () => {
      destTcData[dest].forEach((td: any, tcIdx: number) => {
        it(`TC ${tcIdx + 1}`, async () => {
          if (td.result === true) {
            expect(validateConfig(dest, td.config, "destinations", true)).toBeUndefined();
          } else {
            expect(() => {
              validateConfig(dest, td.config, "destinations", true);
            }).toThrow(JSON.stringify(td.err));
          }
        });
      });
    });
  });

  // Source tests
  Object.keys(srcTcData).forEach((src: any, srcIdx: number) => {
    describe(`${srcIdx + 1}. Source - ${src}`, () => {
      srcTcData[src].forEach((td: any, tcIdx: number) => {
        it(`TC ${tcIdx + 1}`, async () => {
          if (td.result === true) {
            expect(validateConfig(src, td.config, "sources", true)).toBeUndefined();
          } else {
            expect(() => {
              validateConfig(src, td.config, "sources", true);
            }).toThrow(JSON.stringify(td.err));
          }
        });
      });
    });
  });
});
