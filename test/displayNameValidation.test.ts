/* eslint-disable no-console */
import fs from 'fs';
import path from 'path';

/**
 * Test suite to validate that displayName values in destination definitions
 * do not change, as they are used by other features and changing them would
 * impact existing connections.
 */

const destinationsDir = path.resolve('src/configurations/destinations');
const baselineFile = path.resolve('test/data/displayName-baseline.json');

interface DisplayNameBaseline {
  [destinationName: string]: {
    displayName: string;
    directory: string;
  };
}

interface DestinationConfig {
  name: string;
  displayName: string;
}

function loadBaseline(): DisplayNameBaseline {
  if (!fs.existsSync(baselineFile)) {
    throw new Error(
      `DisplayName baseline file not found: ${baselineFile}. ` +
        'Run "node scripts/updateDisplayNameBaseline.js" to generate it.',
    );
  }

  const baselineContent = fs.readFileSync(baselineFile, 'utf8');
  return JSON.parse(baselineContent);
}

function getCurrentDestinations(): Map<string, DestinationConfig> {
  const destinations = new Map<string, DestinationConfig>();

  if (!fs.existsSync(destinationsDir)) {
    throw new Error(`Destinations directory not found: ${destinationsDir}`);
  }

  const destDirs = fs
    .readdirSync(destinationsDir)
    .filter((file) => fs.statSync(path.join(destinationsDir, file)).isDirectory());

  destDirs.forEach((destDir) => {
    const dbConfigPath = path.join(destinationsDir, destDir, 'db-config.json');

    if (!fs.existsSync(dbConfigPath)) {
      return; // Skip if no db-config.json
    }

    try {
      const dbConfigContent = fs.readFileSync(dbConfigPath, 'utf8');
      const dbConfig = JSON.parse(dbConfigContent);

      if (dbConfig.name && dbConfig.displayName) {
        destinations.set(dbConfig.name, {
          name: dbConfig.name,
          displayName: dbConfig.displayName,
        });
      }
    } catch (err) {
      console.warn(`Error reading ${dbConfigPath}:`, err);
    }
  });

  return destinations;
}

describe('DisplayName Validation Tests', () => {
  let baseline: DisplayNameBaseline;
  let currentDestinations: Map<string, DestinationConfig>;

  beforeAll(() => {
    baseline = loadBaseline();
    currentDestinations = getCurrentDestinations();
  });

  it('should have a valid baseline file', () => {
    expect(baseline).toBeDefined();
    expect(Object.keys(baseline).length).toBeGreaterThan(0);
  });

  it('should not allow changes to existing destination displayNames', () => {
    const changedDisplayNames: Array<{
      name: string;
      directory: string;
      baseline: string;
      current: string;
    }> = [];

    // Check each destination in the baseline
    Object.entries(baseline).forEach(([destinationName, baselineData]) => {
      const currentDest = currentDestinations.get(destinationName);

      if (currentDest && currentDest.displayName !== baselineData.displayName) {
        changedDisplayNames.push({
          name: destinationName,
          directory: baselineData.directory,
          baseline: baselineData.displayName,
          current: currentDest.displayName,
        });
      }
    });

    if (changedDisplayNames.length > 0) {
      const errorMessage = [
        '❌ DisplayName changes detected! DisplayNames cannot be changed as they are used by other features.',
        'The following destinations have changed displayNames:',
        '',
        ...changedDisplayNames.map(
          (change) =>
            `  • ${change.name} (${change.directory}/):\n` +
            `    Baseline: "${change.baseline}"\n` +
            `    Current:  "${change.current}"`,
        ),
        '',
        'If you need to change a displayName:',
        '1. Ensure all dependent systems can handle the change',
        '2. Update the baseline by running: node scripts/updateDisplayNameBaseline.js',
        '3. Coordinate with teams that depend on these displayNames',
        '',
        'For new destinations, the baseline will be automatically updated on the next run.',
      ].join('\n');

      throw new Error(errorMessage);
    }
  });

  it('should detect new destinations not in baseline', () => {
    const newDestinations: string[] = [];

    currentDestinations.forEach((dest, name) => {
      if (!baseline[name]) {
        newDestinations.push(name);
      }
    });

    if (newDestinations.length > 0) {
      console.log(`ℹ️  New destinations detected (not in baseline): ${newDestinations.join(', ')}`);
      console.log(
        'Run "node scripts/updateDisplayNameBaseline.js" to update the baseline with new destinations.',
      );
    }

    // This is informational, not a failure
    expect(true).toBe(true);
  });

  it('should detect removed destinations', () => {
    const removedDestinations: Array<{
      name: string;
      directory: string;
      displayName: string;
    }> = [];

    Object.entries(baseline).forEach(([destinationName, baselineData]) => {
      if (!currentDestinations.has(destinationName)) {
        removedDestinations.push({
          name: destinationName,
          directory: baselineData.directory,
          displayName: baselineData.displayName,
        });
      }
    });

    if (removedDestinations.length > 0) {
      console.log(
        `ℹ️  Removed destinations detected: ${removedDestinations.map((d) => d.name).join(', ')}`,
      );
      console.log('Run "node scripts/updateDisplayNameBaseline.js" to update the baseline.');
    }

    // This is informational, not a failure
    expect(true).toBe(true);
  });

  it('should validate baseline integrity', () => {
    // Ensure baseline has required structure
    Object.entries(baseline).forEach(([, data]) => {
      expect(data).toHaveProperty('displayName');
      expect(data).toHaveProperty('directory');
      expect(typeof data.displayName).toBe('string');
      expect(typeof data.directory).toBe('string');
      expect(data.displayName.length).toBeGreaterThan(0);
      expect(data.directory.length).toBeGreaterThan(0);
    });
  });
});
