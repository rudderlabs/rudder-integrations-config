#!/usr/bin/env node
/* eslint-disable no-console */
/* eslint-disable import/no-commonjs */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable no-plusplus */
/* eslint-disable no-restricted-syntax */

const { execSync } = require('child_process');
const path = require('path');

/**
 * Validates that displayName fields in destination db-config.json files
 * have not been changed in the git diff.
 *
 * This script can be used in:
 * - Pre-commit hooks (checks staged changes)
 * - GitHub workflows (checks PR diff against base branch)
 *
 * Exit codes:
 * 0 - No displayName changes detected
 * 1 - DisplayName changes detected (blocking)
 * 2 - Script error
 */

const CONFIG_PATH_PATTERN = 'src/configurations/destinations/*/db-config.json';

/**
 * Get the git diff for destination db-config.json files
 * @param {string} compareRef - Reference to compare against (e.g., 'HEAD', 'origin/main')
 * @param {boolean} staged - If true, check staged changes only
 */
function getGitDiff(compareRef = null, staged = false) {
  try {
    let command;

    if (staged) {
      // For pre-commit: check staged changes
      command = `git diff --cached --unified=0 -- ${CONFIG_PATH_PATTERN}`;
    } else if (compareRef) {
      // For PR/CI: compare against a reference
      command = `git diff ${compareRef} --unified=0 -- ${CONFIG_PATH_PATTERN}`;
    } else {
      // Default: check all uncommitted changes
      command = `git diff HEAD --unified=0 -- ${CONFIG_PATH_PATTERN}`;
    }

    const diff = execSync(command, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
    return diff;
  } catch (error) {
    if (error.status === 0 || error.stdout) {
      // Command succeeded but returned non-zero (no diff)
      return '';
    }
    console.error('Error getting git diff:', error.message);
    throw error;
  }
}

/**
 * Parse git diff to find displayName changes
 * @param {string} diff - Git diff output
 */
function parseDisplayNameChanges(diff) {
  if (!diff || diff.trim() === '') {
    return [];
  }

  const changes = [];
  const lines = diff.split('\n');
  let currentFile = null;
  let removedDisplayName = null;
  let addedDisplayName = null;

  for (const line of lines) {
    // Track which file we're looking at
    if (line.startsWith('diff --git')) {
      // Save previous file's changes if any
      if (currentFile && (removedDisplayName || addedDisplayName)) {
        changes.push({
          file: currentFile,
          removed: removedDisplayName,
          added: addedDisplayName,
        });
      }

      // Extract file path
      const match = line.match(/b\/(.*)/);
      if (match) {
        [, currentFile] = match;
        removedDisplayName = null;
        addedDisplayName = null;
      }
    }

    // Look for displayName changes
    if (line.startsWith('-') && line.includes('"displayName"')) {
      // Removed line with displayName
      const displayNameMatch = line.match(/"displayName":\s*"([^"]*)"/);
      if (displayNameMatch) {
        [, removedDisplayName] = displayNameMatch;
      }
    } else if (line.startsWith('+') && line.includes('"displayName"')) {
      // Added line with displayName
      const displayNameMatch = line.match(/"displayName":\s*"([^"]*)"/);
      if (displayNameMatch) {
        [, addedDisplayName] = displayNameMatch;
      }
    }
  }

  // Don't forget the last file
  if (currentFile && (removedDisplayName || addedDisplayName)) {
    changes.push({
      file: currentFile,
      removed: removedDisplayName,
      added: addedDisplayName,
    });
  }

  // Filter out changes where displayName was only added (new destinations)
  // We only care about modifications to existing displayNames
  return changes.filter(
    (change) => change.removed && change.added && change.removed !== change.added,
  );
}

/**
 * Extract destination name from file path
 */
function getDestinationName(filePath) {
  const match = filePath.match(/destinations\/([^/]+)\//);
  return match ? match[1] : path.basename(path.dirname(filePath));
}

/**
 * Main validation function
 */
function validateDisplayNameChanges(options = {}) {
  const { compareRef = null, staged = false, verbose = true } = options;

  if (verbose) {
    console.log('🔍 Checking for displayName changes...');
    if (staged) {
      console.log('📋 Scope: Staged changes (pre-commit)');
    } else if (compareRef) {
      console.log(`📋 Scope: Changes compared to ${compareRef}`);
    } else {
      console.log('📋 Scope: All uncommitted changes');
    }
  }

  let diff;
  try {
    diff = getGitDiff(compareRef, staged);
  } catch (error) {
    console.error('❌ Failed to get git diff');
    return { success: false, changes: [], error: error.message };
  }

  if (!diff || diff.trim() === '') {
    if (verbose) {
      console.log('✅ No changes to destination configuration files');
    }
    return { success: true, changes: [] };
  }

  const changes = parseDisplayNameChanges(diff);

  if (changes.length === 0) {
    if (verbose) {
      console.log('✅ No displayName changes detected');
    }
    return { success: true, changes: [] };
  }

  // DisplayName changes detected - this is an error
  console.error('\n❌ DisplayName changes detected!');
  console.error('═══════════════════════════════════════════════════════════════\n');
  console.error('DisplayNames cannot be changed as they are used by other features');
  console.error('and changing them will break existing connections.\n');

  console.error('The following displayName changes were found:\n');

  changes.forEach((change, index) => {
    const destName = getDestinationName(change.file);
    console.error(`${index + 1}. ${destName} (${change.file})`);
    console.error(`   Old: "${change.removed}"`);
    console.error(`   New: "${change.added}"`);
    console.error('');
  });

  console.error('═══════════════════════════════════════════════════════════════');
  console.error('\nWhat to do:');
  console.error('  1. Revert the displayName changes in the files listed above');
  console.error('  2. If you must change a displayName:');
  console.error('     - Coordinate with all dependent teams');
  console.error('     - Update all systems that use these displayNames');
  console.error('     - Document the change thoroughly');
  console.error('     - Get approval from tech leads\n');

  return { success: false, changes };
}

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);

  const options = {
    staged: args.includes('--staged'),
    compareRef: null,
    verbose: !args.includes('--quiet'),
  };

  // Look for compare ref (e.g., --compare origin/main)
  const compareIndex = args.indexOf('--compare');
  if (compareIndex !== -1 && args[compareIndex + 1]) {
    options.compareRef = args[compareIndex + 1];
  }

  // Check if we should use default base branch for PR context
  if (args.includes('--pr')) {
    // In PR context, compare against the merge base with main/master
    try {
      const baseBranch = process.env.GITHUB_BASE_REF || 'origin/main';
      options.compareRef = baseBranch;
      console.log(`🔀 PR mode: Comparing against ${baseBranch}`);
    } catch (error) {
      console.warn('⚠️  Could not determine base branch, using origin/main');
      options.compareRef = 'origin/main';
    }
  }

  const result = validateDisplayNameChanges(options);

  if (!result.success) {
    process.exit(1);
  }

  process.exit(0);
}

module.exports = { validateDisplayNameChanges, parseDisplayNameChanges, getGitDiff };
