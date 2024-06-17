/* eslint-disable @typescript-eslint/no-var-requires */
const { JsonTemplateEngine } = require('@rudderstack/json-template-engine');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const readdir = promisify(fs.readdir);
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

const srcPath = path.resolve(__dirname, '../src');

async function getUiConfigTemplate(destinationName) {
  const uiConfig = await readFile(
    `${srcPath}/configurations/destinations/${destinationName}/ui-config.jt`,
    'utf8',
  );
  return uiConfig;
}

async function getUiDefaultData(destinationName) {
  try {
    const defaults = await readFile(
      `${srcPath}/configurations/destinations/${destinationName}/ui-default.json`,
      'utf8',
    );
    return JSON.parse(defaults);
  } catch (error) {
    // skip the destination if ui-default.json is not present
    console.log(`ui-default.json not found for ${destinationName}`);
    return undefined;
  }
}

async function getDestinationNames() {
  const destinationFolders = await readdir(`${srcPath}/configurations/destinations`);
  return destinationFolders;
}

async function main() {
  const destinationFolders = await getDestinationNames();

  destinationFolders.forEach(async (destinationName) => {
    const uiDefaults = await getUiDefaultData(destinationName);
    if (!uiDefaults) {
      return;
    }

    const uiConfigTemplate = await getUiConfigTemplate(destinationName);
    const result = await JsonTemplateEngine.create(uiConfigTemplate).evaluate(uiDefaults);

    await writeFile(
      `${srcPath}/configurations/destinations/${destinationName}/ui-config.json`,
      JSON.stringify(result, null, 2),
    );
  });
}

main().catch((error) => {
  console.error(error);
});
