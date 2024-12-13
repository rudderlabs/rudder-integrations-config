/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');

const destinationsDir = path.join(__dirname, '../src/configurations/destinations');

function findJsonMapperDestinations() {
  try {
    if (!fs.existsSync(destinationsDir)) {
      throw new Error(`Destinations directory not found: ${destinationsDir}`);
    }
    return fs
      .readdirSync(destinationsDir)
      .map((destination) => {
        try {
          const destinationsFilePath = path.join(destinationsDir, destination, 'db-config.json');
          if (!fs.existsSync(destinationsFilePath)) {
            console.warn(`Skipping ${destination}: Missing configuration file`);
            return null;
          }
          const destinationsContent = fs.readFileSync(destinationsFilePath, 'utf8');
          const destinationDefinition = JSON.parse(destinationsContent);
          if (!destinationDefinition.name) {
            console.warn(`Skipping ${destination}: Missing name`);
            return null;
          }
          return {
            name: destinationDefinition.name,
            config: destinationDefinition.config,
          };
        } catch (err) {
          console.error(`Error processing ${destination}:`, err.message);
          return null;
        }
      })
      .filter(Boolean)
      .filter(
        (destination) =>
          !destination.config?.disableJsonMapper && !destination.config?.supportsVisualMapper,
      )
      .map((destination) => destination.name);
  } catch (err) {
    console.error('Failed to process destinations:', err.message);
    return [];
  }
}

console.log(findJsonMapperDestinations().join('\n'));
