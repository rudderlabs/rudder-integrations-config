import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

// Export the pattern that indicates dynamic config support
export const DYNAMIC_CONFIG_REGEX = /\(\^\\+{\\+{\.\*\\+\|\\+\|\(\.\*\)\\+}\\+}\$\)\|/;

export const removeDefaultSubRegex = (regex: string | undefined): string | undefined => {
  if (!regex) return regex;

  // Use the exported pattern
  return regex.replace(DYNAMIC_CONFIG_REGEX, '');
};

export const hasDynamicConfigSupport = (pattern: string): boolean =>
  DYNAMIC_CONFIG_REGEX.test(pattern);

export const postProcessing = async (): Promise<void> => {
  try {
    console.log('Running formatting commands...');
    await execPromise('npm run format');
    console.log('✅ Formatting complete!');
  } catch (error) {
    console.error(
      '❌ Error running formatting commands:',
      error instanceof Error ? error.message : String(error),
    );
  }
};
