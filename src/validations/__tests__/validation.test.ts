/* eslint-disable max-len */
import init, { validateConfig } from '../validator';
import fs from 'fs';
import path from 'path';

type TestConfigSchema = {
  [key: string]: unknown;
};

function getDestNames(path:any) {
  return fs.readdirSync(path).filter(function (file) {
    return fs.statSync(path+'/'+file).isDirectory();
  });
}

// dynamically fetch all the destination names
const destNameArray = getDestNames(path.join(process.cwd(),'data','destinations'));

const testDatas: Array<TestConfigSchema> = [];

// console.log(destNameArray)

destNameArray.forEach((dest: any) => {
  try {
    testDatas[dest] = JSON.parse(
        fs.readFileSync(
            path.resolve(
                __dirname,
                `./validation_test_data/${dest.toLowerCase()}_test.json`,
            ),
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
  Object.keys(testDatas).forEach((dest: any) => {
    let payloadCount = 0;
    describe(`${destCount}. ${dest}`, () => {
      Object.values(testDatas[dest]).forEach((td: any) => {
        it(`Payload ${payloadCount}`, async () => {
          if (td.result === true) {
            expect(validateConfig(dest, td.config)).toBeUndefined();
          }
          if (td.result === false) {
            try {
              validateConfig(dest, td.config);
            } catch (err: any) {
              expect(err.message).toEqual(JSON.stringify(td.err));
            }
          }
        });
        payloadCount += 1;
      });
      destCount += 1;
    });
  });
});
