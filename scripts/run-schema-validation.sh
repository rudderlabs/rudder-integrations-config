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
        selector=$(echo "$selector" | sed 's/.$//')
        # Storing the last directory to ensure that validation runs only once, even if multiple configuration files are changed for a given source or destination.
        if [ "$last_directory" != "${directory}" ]; then
            output==$(python scripts/schemaGenerator.py -name="$name" $selector 2>&1)
            warnings=$(echo "$output" | grep -i "warning" || true)
            recommendations=$(echo "$output" | grep -i "recommendation" || true)
            if [ -n "$warnings" ]; then
                echo "Warnings found for name: ${name} selector: ${selector}:"
                echo "$output"
                exit_code=1
            fi
            if [ -n "$recommendations" ] && [ -z "$warnings" ]; then
                echo "For name: ${name} selector: ${selector}:"
                echo "$output"
            fi
        fi
        last_directory=${directory}
    fi
done
exit $exit_code
