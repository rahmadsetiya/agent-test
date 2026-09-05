#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
backup_dir_input="${BACKUP_DIR:-"$project_root/../agent-test-backups"}"
retention_count="${BACKUP_RETENTION_COUNT:-7}"

if [[ ! "$retention_count" =~ ^[1-9][0-9]*$ ]]; then
    echo "BACKUP_RETENTION_COUNT must be a positive integer." >&2
    exit 1
fi

backup_dir="$(realpath -m -- "$backup_dir_input")"
case "$backup_dir" in
    /|"$project_root"|"$project_root"/*)
        echo "Backup directory must be outside the repository." >&2
        exit 1
        ;;
esac

backup_files=(
    .dockerignore
    .github/workflows/ci.yml
    .gitignore
    AGENTS.md
    Dockerfile
    README.md
    compose.staging.yml
    compose.yml
    hello.py
    scripts/backup.sh
    systemd/agent-test-backup.service
    systemd/agent-test-backup.timer
    test_backup.py
    test_hello.py
    test_systemd.py
)

for file in "${backup_files[@]}"; do
    if [[ ! -f "$project_root/$file" ]]; then
        echo "Required backup file is missing: $file" >&2
        exit 1
    fi
done

mkdir -p -- "$backup_dir"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
archive_path="$backup_dir/agent-test-$timestamp.tar.gz"
if [[ -e "$archive_path" ]]; then
    echo "Backup archive already exists: $archive_path" >&2
    exit 1
fi

tar -czf "$archive_path" -C "$project_root" "${backup_files[@]}"

mapfile -t archives < <(
    find "$backup_dir" -maxdepth 1 -type f \
        -name 'agent-test-????????T??????Z.tar.gz' -printf '%f\n' \
        | LC_ALL=C sort -r
)

for ((index = retention_count; index < ${#archives[@]}; index++)); do
    rm -- "$backup_dir/${archives[$index]}"
done

printf '%s\n' "$archive_path"
