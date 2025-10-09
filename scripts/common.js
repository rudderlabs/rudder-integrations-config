const languageMap = {
  web: ['ts', 'js'],
  flutter: ['dart'],
  ios: ['m', 'swift'],
  android: ['kt', 'java'],
  kotlinAndroid: ['kt', 'java'],
};

// Function to check if the template should be generated for a specific language
function filterLanguages(destination, langCode) {
  if (!destination?.config?.supportedConnectionModes) {
    console.warn(`Destination ${destination.name} is missing supportedConnectionModes`);
    return false;
  }
  const { supportedConnectionModes } = destination.config;

  // Filtering logic
  return Object.keys(supportedConnectionModes)
    .filter((platform) => {
      const modes = supportedConnectionModes[platform];
      // Check if "device" or "hybrid" mode is present
      return modes.includes('device') || modes.includes('hybrid');
    })
    .some((platform) => languageMap[platform]?.includes(langCode));
}

module.exports = {
  filterLanguages,
};
