/* eslint-disable no-console */
/* eslint-disable import/no-commonjs */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable no-plusplus */
const fs = require('fs');
const path = require('path');

const destinationsDir = path.join(__dirname, '../src/configurations/destinations');
const baselineFile = path.join(__dirname, '../test/data/displayName-baseline.json');

/**
 * Update a baseline file containing destination displayNames
 * By default, only adds new destinations (safe for pre-commit)
 * Use --override flag to regenerate the entire baseline
 */
function updateDisplayNameBaseline(overrideExisting = false) {
  try {
    if (!fs.existsSync(destinationsDir)) {
      throw new Error(`Destinations directory not found: ${destinationsDir}`);
    }

    // Load existing baseline if it exists and we're not overriding
    let displayNameBaseline = {};
    let existingCount = 0;

    if (!overrideExisting && fs.existsSync(baselineFile)) {
      const existingContent = fs.readFileSync(baselineFile, 'utf8');
      displayNameBaseline = JSON.parse(existingContent);
      existingCount = Object.keys(displayNameBaseline).length;
      console.log(`📋 Loaded existing baseline with ${existingCount} destinations`);
    } else if (overrideExisting) {
      console.log('🔄 Override mode: Regenerating entire baseline');
    } else {
      console.log('🆕 Creating new baseline file');
    }

    const destinations = fs
      .readdirSync(destinationsDir)
      .filter((file) => fs.statSync(path.join(destinationsDir, file)).isDirectory());

    console.log(`📁 Processing ${destinations.length} destination directories...`);

    let addedCount = 0;
    let skippedCount = 0;
    let updatedCount = 0;

    destinations.forEach((destination) => {
      try {
        const dbConfigPath = path.join(destinationsDir, destination, 'db-config.json');

        if (!fs.existsSync(dbConfigPath)) {
          console.warn(`⚠️  Skipping ${destination}: Missing db-config.json`);
          skippedCount++;
          return;
        }

        const dbConfigContent = fs.readFileSync(dbConfigPath, 'utf8');
        const dbConfig = JSON.parse(dbConfigContent);

        if (!dbConfig.displayName) {
          console.warn(`⚠️  Skipping ${destination}: Missing displayName`);
          skippedCount++;
          return;
        }

        if (!dbConfig.name) {
          console.warn(`⚠️  Skipping ${destination}: Missing name`);
          skippedCount++;
          return;
        }

        const isExisting = displayNameBaseline[dbConfig.name];

        if (isExisting && !overrideExisting) {
          // Don't modify existing destinations unless override is specified
          return;
        }

        displayNameBaseline[dbConfig.name] = {
          displayName: dbConfig.displayName,
          directory: destination,
        };

        if (isExisting) {
          console.log(`🔄 ${destination}: ${dbConfig.displayName} (updated)`);
          updatedCount++;
        } else {
          console.log(`✅ ${destination}: ${dbConfig.displayName} (new)`);
          addedCount++;
        }
      } catch (err) {
        console.error(`❌ Error processing ${destination}:`, err.message);
        skippedCount++;
      }
    });

    // Only write if there are changes or it's a new file
    const totalCount = Object.keys(displayNameBaseline).length;
    const hasChanges = addedCount > 0 || updatedCount > 0 || !fs.existsSync(baselineFile);

    if (hasChanges) {
      // Ensure the test/data directory exists
      const testDataDir = path.dirname(baselineFile);
      if (!fs.existsSync(testDataDir)) {
        fs.mkdirSync(testDataDir, { recursive: true });
      }

      // Write the baseline file
      fs.writeFileSync(baselineFile, JSON.stringify(displayNameBaseline, null, 2));

      console.log(`\n🎉 Baseline file updated successfully!`);
      console.log(`📁 Location: ${baselineFile}`);
      console.log(`📊 Total destinations: ${totalCount}`);

      if (overrideExisting) {
        console.log(`🔄 Regenerated entire baseline (${updatedCount} updated, ${addedCount} new)`);
      } else {
        console.log(
          `🆕 Added ${addedCount} new destinations (${existingCount} existing preserved)`,
        );
      }
    } else {
      console.log(`\n✅ Baseline is up to date!`);
      console.log(`📊 Total destinations: ${totalCount}`);
      console.log(`🆕 No new destinations found`);
    }

    if (skippedCount > 0) {
      console.log(`⚠️  Skipped ${skippedCount} destinations (see warnings above)`);
    }

    return {
      baseline: displayNameBaseline,
      stats: {
        total: totalCount,
        added: addedCount,
        updated: updatedCount,
        skipped: skippedCount,
        hasChanges,
      },
    };
  } catch (err) {
    console.error('❌ Failed to generate displayName baseline:', err.message);
    throw err;
  }
}

// Run the script if called directly
if (require.main === module) {
  const args = process.argv.slice(2);
  const overrideExisting = args.includes('--override');

  if (overrideExisting) {
    console.log('🔄 Running in override mode - will regenerate entire baseline');
  } else {
    console.log('🛡️  Running in safe mode - will only add new destinations');
  }

  updateDisplayNameBaseline(overrideExisting);
}

module.exports = { updateDisplayNameBaseline };
