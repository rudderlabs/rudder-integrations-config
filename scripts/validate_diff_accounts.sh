#!/bin/bash

# Pre-commit hook to validate account definitions
# This script checks that all rudderAccountId values in destination configs
# have corresponding account configuration files.

# Get the list of changed files
changed_files=$(git diff --cached --name-only)


# Extract unique destination names from changed files
destinations=()

for file in $changed_files; do
  if [[ $file =~ src/configurations/destinations/([^/]+)/db-config\.json ]]; then
    # Main destination config file changed
    dest="${BASH_REMATCH[1]}"
    if [[ ! " ${destinations[@]} " =~ " ${dest} " ]]; then
      destinations+=("$dest")
    fi
  elif [[ $file =~ src/configurations/destinations/([^/]+)/accounts/ ]]; then
    # Account config file changed
    dest="${BASH_REMATCH[1]}"
    if [[ ! " ${destinations[@]} " =~ " ${dest} " ]]; then
      destinations+=("$dest")
    fi
  fi
done

# If no relevant files changed, exit successfully
if [ ${#destinations[@]} -eq 0 ]; then
  echo "No destination configuration files changed. Skipping validation."
  exit 0
fi

# Make the Python script executable
chmod +x scripts/validate_account_definitions.py

# Validate each changed destination
exit_code=0
for dest in "${destinations[@]}"; do
  echo "Validating account definitions for destination: $dest"
  python3 scripts/validate_account_definitions.py "$dest"
  if [ $? -ne 0 ]; then
    exit_code=1
  fi
done

if [ $exit_code -ne 0 ]; then
  echo "❌ Validation failed. Please fix the issues before committing."
  echo "   Make sure all rudderAccountId values in destination configs have corresponding account configurations."
else
  echo "✅ Account validation passed."
fi

exit $exit_code
