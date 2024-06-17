/* eslint-disable @typescript-eslint/no-var-requires */
const { JsonTemplateEngine } = require('@rudderstack/json-template-engine');
const fs = require('fs');
const path = require('path');

const srcPath = path.resolve(__dirname, '../src');

function getUiConfigTemplate(destinationName) {
  const uiConfig = fs.readFileSync(
    `${srcPath}/configurations/destinations/${destinationName}/ui-config.jt`,
    'utf8',
  );
  return uiConfig;
}

function getUiDefaultData(destinationName) {
  try {
    const defaults = fs.readFileSync(
      `${srcPath}/configurations/destinations/${destinationName}/ui-default.json`,
      'utf8',
    );
    return JSON.parse(defaults);
  } catch (error) {
    // skip the destination if ui-default.json is not present
    return undefined;
  }
}

function getDestinationNames() {
  // read all the ui-config files from src/destinations/{destinationName} folder

  // resolve path to src from current directory

  const destinationFolders = fs
    .readdirSync(`${srcPath}/configurations/destinations`, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .map((dirent) => dirent.name);

  return destinationFolders;
}

function main() {
  const destinationFolders = getDestinationNames();

  destinationFolders.forEach((destinationName) => {
    const uiDefaults = getUiDefaultData(destinationName);
    if (!uiDefaults) {
      return;
    }

    const uiConfigTemplate = getUiConfigTemplate(destinationName);
    const result = JsonTemplateEngine.createAsSync(uiConfigTemplate).evaluate(uiDefaults);

    fs.writeFileSync(
      `${srcPath}/configurations/destinations/${destinationName}/ui-config.json`,
      JSON.stringify(result, null, 2),
    );
  });
}

main();
