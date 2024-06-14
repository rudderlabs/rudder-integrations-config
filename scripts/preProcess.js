/* eslint-disable @typescript-eslint/no-var-requires */
const fs = require('fs');
const path = require('path');

const srcPath = path.resolve(__dirname, '../src');

function updateDefaults(jsonData, configKeyToUpdate, newDefaults) {
  // Helper function for recursive traversal
  function traverse(obj) {
    if (typeof obj === 'object' && obj !== null) {
      // Check for both objects and arrays
      Object.keys(obj).forEach((key) => {
        if (key === 'configKey' && obj[key] === configKeyToUpdate) {
          // Found the object with the specified configKey
          // eslint-disable-next-line dot-notation, no-param-reassign
          obj['default'] = newDefaults;
          return;
        }
        traverse(obj[key]);
      });
    }
  }

  try {
    traverse(jsonData); // Start traversal from the root
  } catch (error) {
    console.error(`Error while updating defaults for ${configKeyToUpdate}: ${error}`);
  }

  return jsonData;
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

function getUiConfigData(destinationName) {
  const uiConfig = fs.readFileSync(
    `${srcPath}/configurations/destinations/${destinationName}/ui-config.json`,
    'utf8',
  );
  return JSON.parse(uiConfig);
}

function getUiDefaults(destinationName) {
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

function main() {
  const destinationFolders = getDestinationNames();

  destinationFolders.forEach((destinationName) => {
    const uiDefaults = getUiDefaults(destinationName);
    if (!uiDefaults) {
      return;
    }
    const uiConfigData = getUiConfigData(destinationName);

    // update the defaults in ui-config.json
    Object.keys(uiDefaults).forEach((key) => {
      const defaultVal = uiDefaults[key];
      const updatedUIConfigData = updateDefaults(uiConfigData, key, defaultVal);

      console.log(`Updating defaults for ${key} in ${destinationName}`);
      fs.writeFileSync(
        `${srcPath}/configurations/destinations/${destinationName}/ui-config.json`,
        JSON.stringify(updatedUIConfigData, null, 2),
      );
    });
  });
}

main();
