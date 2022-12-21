/* eslint-disable max-len */
import { init, validateConfig } from '../src';
import fs from 'fs';
import path from 'path';

type TestConfigSchema = {
  [key: string]: unknown;
};

function getDestNames(path: any) {
  return fs.readdirSync(path).filter(function (file) {
    return fs.statSync(path + '/' + file).isDirectory();
  });
}

// dynamically fetch all the destination names
const destNameArray = getDestNames(path.resolve('src/configurations/destinations'));

const testData: Array<TestConfigSchema> = [];

// console.log(destNameArray)

destNameArray.forEach((dest: any) => {
  try {
    testData[dest] = JSON.parse(
      fs.readFileSync(
        path.resolve(__dirname, `./validation_test_data/${dest.toLowerCase()}_test.json`),
        'utf-8',
      ),
    );
  } catch (e) {}
});

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

describe('Validator Tests', () => {
  beforeAll(async () => {
    init();
    await delay(1000);
  });
  let destCount = 1;
  Object.keys(testData).forEach((dest: any) => {
    let payloadCount = 0;
    describe(`${destCount}. ${dest}`, () => {
      Object.values(testData[dest]).forEach((td: any) => {
        it(`Payload ${payloadCount}`, async () => {
          if (td.result === true) {
            expect(validateConfig(dest, td.config, true)).toBeUndefined();
          }
          if (td.result === false) {
            expect(() => {
              validateConfig(dest, td.config, true);
            }).toThrow(JSON.stringify(td.err));
          }
        });
        payloadCount += 1;
      });
      destCount += 1;
    });
  });
});
