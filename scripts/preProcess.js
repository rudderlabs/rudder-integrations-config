/* eslint-disable @typescript-eslint/no-var-requires */
const { JsonTemplateEngine } = require('@rudderstack/json-template-engine');
const fs = require('fs/promises');
const path = require('path');

const srcPath = path.resolve(__dirname, '../src');

async function getUiConfigTemplate(destinationName) {
  const uiConfig = await fs.readFile(
    `${srcPath}/configurations/destinations/${destinationName}/ui-config.jt`,
    'utf8',
  );
  return uiConfig;
}

async function getUiDefaultData(destinationName) {
  try {
    const defaults = await fs.readFile(
      `${srcPath}/configurations/destinations/${destinationName}/ui-default.json`,
      'utf8',
    );
    return JSON.parse(defaults);
  } catch (error) {
    // skip the destination if ui-default.json is not present
    // console.debug(`ui-default.json not found for ${destinationName}`);
    return undefined;
  }
}

async function getDestinationNames() {
  const destinationFolders = await fs.readdir(`${srcPath}/configurations/destinations`);
  return destinationFolders;
}

async function main() {
  const destinationFolders = await getDestinationNames();

  for (const destinationName of destinationFolders) {
    if (destinationName === 'ga4_v2') {
      // console.debug('Skipping GA4_v2');
      continue;
    }
    const uiDefaults = await getUiDefaultData(destinationName);
    if (!uiDefaults) {
      continue;
    }

    const uiConfigTemplate = await getUiConfigTemplate(destinationName);
    const result = await JsonTemplateEngine.create(uiConfigTemplate).evaluate(uiDefaults);

    await fs.writeFile(
      `${srcPath}/configurations/destinations/${destinationName}/ui-config.json`,
      JSON.stringify(result, null, 2),
    );
  }
}

main().catch((error) => {
  console.error(error);
});
