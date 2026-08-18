#!/bin/bash

# Checks that the source/destination configs touched by a PR do not introduce *new*
# schema-generator drift.
#
# The generator emits a UserWarning for every difference between the committed
# schema.json and the schema it would generate from ui-config.json/db-config.json.
# A large share of the configs in this repo already carry such differences, so
# failing on the mere presence of a warning fails PRs for drift they did not cause.
# Instead we generate the same report against the base branch and only fail on
# warnings that are not already there.

set -uo pipefail

base_ref="${BASE_REF:-develop}"
exit_code=0
base_worktree=""
base_tmp_dir=""

cleanup() {
    if [ -n "$base_worktree" ] && [ "$base_worktree" != "__unavailable__" ]; then
        git worktree remove --force "$base_worktree" >/dev/null 2>&1 || true
    fi
    # Only ever remove the directory mktemp handed us, never a path derived from
    # $base_worktree, so a surprising value can't turn this into a wider delete.
    if [ -n "$base_tmp_dir" ]; then
        rm -rf "$base_tmp_dir" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

# Checks out the base branch once, lazily, so PRs that touch no config directory
# (or introduce no warnings) never pay for it.
setup_base_worktree() {
    if [ -n "$base_worktree" ]; then
        return
    fi
    local tmp_dir=""
    if ! tmp_dir=$(mktemp -d) || [ -z "$tmp_dir" ] || [ ! -d "$tmp_dir" ]; then
        echo "Note: could not create a temporary directory; comparing against an empty baseline."
        base_worktree="__unavailable__"
        return
    fi
    base_tmp_dir="$tmp_dir"
    if git worktree add --detach "${tmp_dir}/base" "origin/${base_ref}" >/dev/null 2>&1; then
        base_worktree="${tmp_dir}/base"
    else
        echo "Note: could not check out origin/${base_ref}; comparing against an empty baseline."
        base_worktree="__unavailable__"
    fi
}

run_generator() {
    local root="$1" name="$2" selector="$3"
    (cd "$root" && python scripts/schemaGenerator.py -name="$name" "$selector" 2>&1)
}

# Reduces generator output to a comparable set of warnings. Each warning is
# printed by Python as
#
#   <path>:<line>: UserWarning: <message, frequently spanning several lines>
#     warnings.warn(
#
# so the whole message is folded onto one line: comparing only the first line
# would treat two different diffs for the same field as identical. The
# <path>:<line> prefix is dropped so the comparison survives edits to the
# generator itself.
normalize_warnings() {
    awk '
        /UserWarning: / {
            if (capturing) print block
            sub(/^.*UserWarning: /, "")
            block = $0
            capturing = 1
            next
        }
        capturing && /warnings\.warn\(/ { print block; capturing = 0; next }
        capturing { block = block " " $0 }
        END { if (capturing) print block }
    ' | sed 's/[[:space:]][[:space:]]*/ /g; s/^ //; s/ $//' | sort -u
}

processed_dirs=""

for file in "$@"; do
    directory=$(dirname "$file")
    parent_directory=$(dirname "$directory")

    if [[ "$parent_directory" != "src/configurations/destinations" && "$parent_directory" != "src/configurations/sources" ]]; then
        continue
    fi

    # Validate each directory once, even when a PR changes several of its files.
    case " ${processed_dirs} " in
        *" ${directory} "*) continue ;;
    esac
    processed_dirs="${processed_dirs} ${directory}"

    name=$(basename "$directory")
    selector=$(basename "$parent_directory")
    selector=${selector%s}

    output=$(run_generator "." "$name" "$selector")
    warnings=$(printf '%s\n' "$output" | normalize_warnings)
    recommendations=$(printf '%s\n' "$output" | grep -i "recommendation" || true)

    if [ -z "$warnings" ]; then
        if [ -n "$recommendations" ]; then
            echo "For name: ${name} selector: ${selector}:"
            printf '%s\n' "$output"
        fi
        continue
    fi

    setup_base_worktree
    base_warnings=""
    if [ "$base_worktree" != "__unavailable__" ] && [ -d "${base_worktree}/${directory}" ]; then
        base_warnings=$(run_generator "$base_worktree" "$name" "$selector" | normalize_warnings)
    fi

    new_warnings=$(comm -23 <(printf '%s\n' "$warnings") <(printf '%s\n' "$base_warnings" | sed '/^$/d'))

    if [ -n "$new_warnings" ]; then
        echo "New warnings found for name: ${name} selector: ${selector}:"
        printf '%s\n' "$new_warnings"
        echo ""
        echo "Full generator output for name: ${name} selector: ${selector}:"
        printf '%s\n' "$output"
        exit_code=1
    else
        echo "For name: ${name} selector: ${selector}: pre-existing schema drift matches origin/${base_ref}; no new warnings."
        if [ -n "$recommendations" ]; then
            printf '%s\n' "$recommendations"
        fi
    fi
done

exit $exit_code
