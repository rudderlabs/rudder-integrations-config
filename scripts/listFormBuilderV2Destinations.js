/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');

const destinationsDir = path.join(__dirname, '../src/configurations/destinations');

function findFormBuilderV2Destinations() {
  try {
    if (!fs.existsSync(destinationsDir)) {
      throw new Error(`Destinations directory not found: ${destinationsDir}`);
    }
    return fs
      .readdirSync(destinationsDir)
      .map((destination) => {
        try {
          const destinationsFilePath = path.join(destinationsDir, destination, 'db-config.json');
          const destinationsUIFilePath = path.join(destinationsDir, destination, 'ui-config.json');

          if (!fs.existsSync(destinationsFilePath) || !fs.existsSync(destinationsUIFilePath)) {
            console.warn(`Skipping ${destination}: Missing configuration files`);
            return null;
          }
          const destinationsContent = fs.readFileSync(destinationsFilePath, 'utf8');
          const destinationsUIConfig = fs.readFileSync(destinationsUIFilePath, 'utf8');
          const destinationDefinition = JSON.parse(destinationsContent);
          const destinationUIConfig = JSON.parse(destinationsUIConfig);
          if (!destinationDefinition.displayName) {
            console.warn(`Skipping ${destination}: Missing displayName`);
            return null;
          }
          return {
            displayName: destinationDefinition.displayName,
            uiConfig: destinationUIConfig.uiConfig,
          };
        } catch (err) {
          console.error(`Error processing ${destination}:`, err.message);
          return null;
        }
      })
      .filter(Boolean)
      .filter(
        (destination) => !Array.isArray(destination.uiConfig) && destination.uiConfig?.baseTemplate,
      )
      .map((destination) => destination.displayName);
  } catch (err) {
    console.error('Failed to process destinations:', err.message);
    return [];
  }
}

console.log(findFormBuilderV2Destinations().join('\n'));
