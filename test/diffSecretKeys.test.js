/* eslint-disable @typescript-eslint/no-var-requires */
const { diffSecretKeys } = require('../scripts/diffSecretKeys');

const BEFORE_SHA = 'a'.repeat(40);
const AFTER_SHA = 'b'.repeat(40);
const ZERO_SHA = '0'.repeat(40);
const destinationPath = (destination) =>
  `src/configurations/destinations/${destination}/db-config.json`;
const definition = (secretKeys) =>
  JSON.stringify({ config: secretKeys === undefined ? {} : { secretKeys } });

function createGit(snapshots, inspectionFailure) {
  return jest.fn((args) => {
    const [command] = args;

    if (command === 'cat-file') {
      const revision = args[2].slice(0, -'^{commit}'.length);
      if (!Object.prototype.hasOwnProperty.call(snapshots, revision)) {
        throw new Error(`Unknown revision ${revision}`);
      }
      return '';
    }

    if (command === 'ls-tree') {
      const revision = args[4];
      return `${Object.keys(snapshots[revision]).sort().join('\0')}\0`;
    }

    if (command === 'show') {
      const separator = args[1].indexOf(':');
      const revision = args[1].slice(0, separator);
      const file = args[1].slice(separator + 1);
      if (inspectionFailure?.revision === revision && inspectionFailure.file === file) {
        throw new Error('git show failed');
      }
      return snapshots[revision][file];
    }

    throw new Error(`Unexpected git command: ${args.join(' ')}`);
  });
}

function revisions(before, after) {
  return {
    [BEFORE_SHA]: before,
    [AFTER_SHA]: after,
  };
}

describe('diffSecretKeys', () => {
  test('reports unchanged keys as a no-op', () => {
    const file = destinationPath('example');
    const git = createGit(
      revisions({ [file]: definition(['token']) }, { [file]: definition(['token']) }),
    );

    expect(diffSecretKeys(BEFORE_SHA, AFTER_SHA, git)).toEqual({
      changed: false,
      changedDestinations: [],
    });
  });

  test('ignores secretKeys ordering', () => {
    const file = destinationPath('example');
    const git = createGit(
      revisions(
        { [file]: definition(['credentials.token', 'apiKey']) },
        { [file]: definition(['apiKey', 'credentials.token']) },
      ),
    );

    expect(diffSecretKeys(BEFORE_SHA, AFTER_SHA, git).changed).toBe(false);
  });

  test.each([
    ['added', ['apiKey'], ['apiKey', 'token']],
    ['removed', ['apiKey', 'token'], ['apiKey']],
  ])('detects %s secret keys', (_change, beforeKeys, afterKeys) => {
    const file = destinationPath('example');
    const git = createGit(
      revisions({ [file]: definition(beforeKeys) }, { [file]: definition(afterKeys) }),
    );

    expect(diffSecretKeys(BEFORE_SHA, AFTER_SHA, git)).toEqual({
      changed: true,
      changedDestinations: ['example'],
    });
  });

  test.each([
    ['new', {}, { [destinationPath('new_destination')]: definition(['token']) }],
    ['deleted', { [destinationPath('old_destination')]: definition(['token']) }, {}],
  ])('detects a %s destination', (_change, before, after) => {
    const stableFile = destinationPath('stable');
    const git = createGit(
      revisions(
        { [stableFile]: definition([]), ...before },
        { [stableFile]: definition([]), ...after },
      ),
    );

    expect(diffSecretKeys(BEFORE_SHA, AFTER_SHA, git).changed).toBe(true);
  });

  test('treats an absent secretKeys field as an empty array', () => {
    const file = destinationPath('example');
    const git = createGit(revisions({ [file]: definition() }, { [file]: definition([]) }));

    expect(diffSecretKeys(BEFORE_SHA, AFTER_SHA, git).changed).toBe(false);
  });

  test('fails on malformed JSON', () => {
    const file = destinationPath('example');
    const git = createGit(revisions({ [file]: definition([]) }, { [file]: '{invalid' }));

    expect(() => diffSecretKeys(BEFORE_SHA, AFTER_SHA, git)).toThrow('Unable to inspect or parse');
  });

  test('fails closed when git cannot inspect a listed file', () => {
    const file = destinationPath('example');
    const git = createGit(revisions({ [file]: definition([]) }, { [file]: definition([]) }), {
      revision: AFTER_SHA,
      file,
    });

    expect(() => diffSecretKeys(BEFORE_SHA, AFTER_SHA, git)).toThrow('Unable to inspect or parse');
  });

  test.each([
    ['malformed', 'not-a-sha'],
    ['all-zero', ZERO_SHA],
  ])('rejects the %s revision', (_kind, revision) => {
    const git = createGit(revisions({}, {}));

    expect(() => diffSecretKeys(revision, AFTER_SHA, git)).toThrow(/revision/);
  });

  test('rejects an unavailable commit', () => {
    const git = createGit({ [AFTER_SHA]: {} });

    expect(() => diffSecretKeys(BEFORE_SHA, AFTER_SHA, git)).toThrow(
      'Before revision is not available as a commit',
    );
  });
});
