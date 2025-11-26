#!/usr/bin/env node
/**
 * Validates a single destination without running the full Jest test suite.
 * This allows testing only the destination being updated, not all destinations.
 *
 * Usage: node validate-single-destination.js <destination-name>
 */

const fs = require('fs');
const path = require('path');

// Register ts-node to handle TypeScript imports
require('ts-node/register');

// Get destination name from command line
const destinationName = process.argv[2];

if (!destinationName) {
  console.error('Error: Destination name required');
  console.error('Usage: node validate-single-destination.js <destination-name>');
  process.exit(1);
}

// Import validation functions (TypeScript file)
const { init, validateConfig } = require('../../src/index.ts');

async function validateDestination(destName) {
  try {
    console.log(`Validating destination: ${destName}\n`);

    // Initialize validators
    await init();

    // Load destination config files
    const destDir = path.resolve(__dirname, `../../src/configurations/destinations/${destName}`);

    if (!fs.existsSync(destDir)) {
      console.error(`❌ Destination directory not found: ${destDir}`);
      return false;
    }

    const dbConfigPath = path.join(destDir, 'db-config.json');
    const schemaPath = path.join(destDir, 'schema.json');

    if (!fs.existsSync(dbConfigPath)) {
      console.error(`❌ db-config.json not found`);
      return false;
    }

    if (!fs.existsSync(schemaPath)) {
      console.error(`❌ schema.json not found`);
      return false;
    }

    // Load config
    const dbConfig = JSON.parse(fs.readFileSync(dbConfigPath, 'utf-8'));

    // Load test data if available
    const testDataPath = path.resolve(
      __dirname,
      `../../test/data/validation/destinations/${destName}.json`,
    );
    let testConfigs = [];

    if (fs.existsSync(testDataPath)) {
      testConfigs = JSON.parse(fs.readFileSync(testDataPath, 'utf-8'));
      console.log(`Found ${testConfigs.length} test case(s)\n`);
    } else {
      console.log(`No test data file found at ${testDataPath}`);
      console.log(`Creating minimal test case from db-config.json\n`);

      // Create a minimal test config from db-config
      testConfigs = [
        {
          config: {},
          name: destName,
        },
      ];
    }

    // Validate each test case
    let passed = 0;
    let failed = 0;

    for (let i = 0; i < testConfigs.length; i++) {
      const testData = testConfigs[i];
      const testNum = i + 1;
      const testTitle = testData.testTitle || '';

      try {
        // Check if this test should pass or fail
        const shouldPass = testData.result === true;
        const config = testData.config || testData;

        if (shouldPass) {
          // Test should pass - validation should return undefined
          const validationResult = validateConfig(
            destName,
            config,
            'destinations',
            true, // throw on error
          );

          if (validationResult === undefined) {
            console.log(`✓ Test case ${testNum}${testTitle ? ` - ${testTitle}` : ''}: PASSED`);
            passed++;
          } else {
            console.log(
              `✗ Test case ${testNum}${
                testTitle ? ` - ${testTitle}` : ''
              }: FAILED (unexpected result)`,
            );
            console.log(`  Expected: pass, Got: ${JSON.stringify(validationResult)}`);
            failed++;
          }
        } else {
          // Test should fail - validation should throw an error
          try {
            validateConfig(
              destName,
              config,
              'destinations',
              true, // throw on error
            );

            // If we get here, validation didn't throw (unexpected)
            console.log(
              `✗ Test case ${testNum}${
                testTitle ? ` - ${testTitle}` : ''
              }: FAILED (should have thrown error)`,
            );
            console.log(`  Expected error: ${JSON.stringify(testData.err)}`);
            failed++;
          } catch (validationError) {
            // Validation threw an error as expected
            const expectedError = JSON.stringify(testData.err);
            const actualError = validationError.message;

            if (actualError === expectedError) {
              console.log(
                `✓ Test case ${testNum}${
                  testTitle ? ` - ${testTitle}` : ''
                }: PASSED (error as expected)`,
              );
              passed++;
            } else {
              console.log(
                `✗ Test case ${testNum}${testTitle ? ` - ${testTitle}` : ''}: FAILED (wrong error)`,
              );
              console.log(`  Expected: ${expectedError}`);
              console.log(`  Got: ${actualError}`);
              failed++;
            }
          }
        }
      } catch (error) {
        // Unexpected error during test execution
        console.log(
          `✗ Test case ${testNum}${testTitle ? ` - ${testTitle}` : ''}: FAILED (unexpected error)`,
        );
        console.log(`  Error: ${error.message}`);
        failed++;
      }
    }

    // Summary
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Validation Summary for ${destName}`);
    console.log(`${'='.repeat(60)}`);
    console.log(`✓ Passed: ${passed}`);
    console.log(`✗ Failed: ${failed}`);
    console.log(`Total: ${testConfigs.length}`);
    console.log(`${'='.repeat(60)}\n`);

    return failed === 0;
  } catch (error) {
    console.error(`\n❌ Validation error: ${error.message}`);
    if (error.stack) {
      console.error(error.stack);
    }
    return false;
  }
}

// Run validation
validateDestination(destinationName)
  .then((success) => {
    process.exit(success ? 0 : 1);
  })
  .catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
