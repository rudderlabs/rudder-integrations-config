const { pathsToModuleNameMapper } = require('ts-jest');
const { compilerOptions } = require('./tsconfig.paths.json');

module.exports = {
  coverageDirectory: "coverage",
  moduleNameMapper: {
    ...pathsToModuleNameMapper(compilerOptions.paths, { prefix: '<rootDir>/' })
  },
  preset: "ts-jest",
  testEnvironment: "node",
  testMatch: [
    "**/v1/*/index.test.*[jt]s?(x)"
  ],
  testPathIgnorePatterns: [
    "/node_modules/",
  ],
  watchPathIgnorePatterns: ['node_modules'],
};
