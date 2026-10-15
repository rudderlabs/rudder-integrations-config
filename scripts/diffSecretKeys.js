/* eslint-disable @typescript-eslint/no-var-requires */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');

const DESTINATION_CONFIG_PATTERN = /^src\/configurations\/destinations\/([^/]+)\/db-config\.json$/;
const ZERO_SHA = '0000000000000000000000000000000000000000';

function compareStrings(left, right) {
  if (left < right) {
    return -1;
  }
  if (left > right) {
    return 1;
  }
  return 0;
}

function runGit(args, options = {}) {
  return execFileSync('git', args, {
    encoding: 'utf8',
    maxBuffer: 50 * 1024 * 1024,
    ...options,
  });
}

function validateRevision(name, revision, git = runGit) {
  if (typeof revision !== 'string' || !/^[\dA-Fa-f]{40}$/.test(revision)) {
    throw new Error(`${name} revision is not a 40-character SHA`);
  }

  if (revision === ZERO_SHA) {
    throw new Error(`${name} revision is the all-zero SHA`);
  }

  try {
    git(['cat-file', '-e', `${revision}^{commit}`], { stdio: 'ignore' });
  } catch (error) {
    throw new Error(`${name} revision is not available as a commit`, { cause: error });
  }
}

function normalizeRevision(revision, git = runGit) {
  const files = git([
    'ls-tree',
    '-r',
    '-z',
    '--name-only',
    revision,
    '--',
    'src/configurations/destinations',
  ])
    .split('\0')
    .filter(Boolean)
    .filter((file) => DESTINATION_CONFIG_PATTERN.test(file))
    .sort();

  if (files.length === 0) {
    throw new Error(`No destination db-config.json files found at ${revision}`);
  }

  const mapping = files.reduce((normalizedMapping, file) => {
    const match = DESTINATION_CONFIG_PATTERN.exec(file);
    const destination = match[1].normalize('NFC');

    if (!destination || normalizedMapping.has(destination)) {
      throw new Error(`Invalid or duplicate normalized destination name for ${file}`);
    }

    let definition;
    try {
      definition = JSON.parse(git(['show', `${revision}:${file}`]));
    } catch (error) {
      throw new Error(`Unable to inspect or parse ${file} at ${revision}`, { cause: error });
    }

    if (definition === null || typeof definition !== 'object' || Array.isArray(definition)) {
      throw new Error(`${file} at ${revision} must contain a JSON object`);
    }

    const { config } = definition;
    if (config === null || typeof config !== 'object' || Array.isArray(config)) {
      throw new Error(`${file} at ${revision} must contain an object at config`);
    }

    const secretKeys = Object.prototype.hasOwnProperty.call(config, 'secretKeys')
      ? config.secretKeys
      : [];

    if (!Array.isArray(secretKeys)) {
      throw new Error(`${file} at ${revision} config.secretKeys must be an array`);
    }

    const normalizedSecretKeys = secretKeys
      .map((secretKey, index) => {
        if (typeof secretKey !== 'string') {
          throw new Error(`${file} at ${revision} config.secretKeys[${index}] must be a string`);
        }
        return secretKey.normalize('NFC');
      })
      .sort();

    normalizedMapping.set(destination, normalizedSecretKeys);
    return normalizedMapping;
  }, new Map());

  return Object.fromEntries(
    [...mapping.entries()].sort(([left], [right]) => compareStrings(left, right)),
  );
}

function diffSecretKeys(beforeRevision, afterRevision, git = runGit) {
  validateRevision('Before', beforeRevision, git);
  validateRevision('After', afterRevision, git);

  const before = normalizeRevision(beforeRevision, git);
  const after = normalizeRevision(afterRevision, git);
  const destinations = [...new Set([...Object.keys(before), ...Object.keys(after)])].sort(
    compareStrings,
  );
  const changedDestinations = destinations.filter(
    (destination) =>
      JSON.stringify(before[destination] ?? null) !== JSON.stringify(after[destination] ?? null),
  );

  return {
    changed: changedDestinations.length > 0,
    changedDestinations,
  };
}

function main(args = process.argv.slice(2), env = process.env) {
  if (args.length !== 2) {
    throw new Error('Usage: node scripts/diffSecretKeys.js <before-sha> <after-sha>');
  }

  const result = diffSecretKeys(args[0], args[1]);

  if (env.GITHUB_OUTPUT) {
    fs.appendFileSync(env.GITHUB_OUTPUT, `changed=${result.changed}\n`);
  }

  // eslint-disable-next-line no-console
  console.log(
    result.changed
      ? `secretKeys changed for destinations: ${result.changedDestinations.join(', ')}`
      : 'No normalized secretKeys changes detected.',
  );

  return result;
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(error.message);
    process.exitCode = 1;
  }
}

module.exports = {
  diffSecretKeys,
  main,
  normalizeRevision,
  validateRevision,
};
