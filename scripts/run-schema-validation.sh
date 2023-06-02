#!/bin/bash

changed_files="$1"
exit_code=0
last_directory=""
for file in $changed_files; do
    directory=$(dirname "${file}")
    parent_directory=$(dirname "${directory}")
    if [[ "$parent_directory" == "src/configurations/destinations" || "$parent_directory" == "src/configurations/sources" ]]; then
        name=$(echo "$file" | cut -d '/' -f 4)
        selector=$(echo "$parent_directory" | cut -d '/' -f 3)
        selector=${selector::-1}
        # Storing the last directory to ensure that validation runs only once, even if multiple configuration files are changed for a given source or destination.
        if [ "$last_directory" != "${directory}" ]; then
            warnings=$(python scripts/schemaGenerator.py -name="$name" $selector 2>&1 | grep -i "warning" || true)
            if [ -n "$warnings" ]; then
                echo "Warnings found for name: ${name} selector: ${selector}:"
                echo "$warnings"
                exit_code=1
            fi
        fi
        last_directory=${directory}
    fi
done
exit $exit_code