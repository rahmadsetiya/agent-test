# Agent Test

## Local usage

Run the application:

```bash
python3 hello.py
```

Run the tests:

```bash
python3 -m unittest discover -v
```

## Staging with Docker Compose

Validate the staging configuration:

```bash
docker compose -f compose.staging.yml config
```

Deploy or update staging:

```bash
docker compose -f compose.staging.yml up -d --build
```

Check staging status:

```bash
docker compose -f compose.staging.yml ps
```

The `app` service should report `healthy` after its startup healthcheck passes.

View staging logs:

```bash
docker compose -f compose.staging.yml logs -f
```

Run the healthcheck probe manually:

```bash
docker compose -f compose.staging.yml exec app python hello.py Healthcheck
```

Inspect Docker's health status and healthcheck history:

```bash
docker inspect --format '{{json .State.Health}}' "$(docker compose -f compose.staging.yml ps -q app)"
```

Run the app inside staging:

```bash
docker compose -f compose.staging.yml exec app python hello.py Tyo
```

Run tests inside staging:

```bash
docker compose -f compose.staging.yml exec app python -m unittest discover -v
```

## Backup and restore

Create a timestamped project backup outside the repository:

```bash
./scripts/backup.sh
```

Backups default to `../agent-test-backups`. Override the location or retention
count when needed:

```bash
BACKUP_DIR=/path/outside/agent-test BACKUP_RETENTION_COUNT=7 ./scripts/backup.sh
```

List available backups and select the newest archive:

```bash
ls -lh ../agent-test-backups
archive="$(ls -1t ../agent-test-backups/agent-test-*.tar.gz | head -n 1)"
```

List the files stored in an archive:

```bash
tar -tzf "$archive"
```

Restore into a temporary directory without overwriting the working tree:

```bash
restore_dir="$(mktemp -d)"
tar -xzf "$archive" -C "$restore_dir"
find "$restore_dir" -type f -print | sort
```

Verify every restored file against the current project:

```bash
while IFS= read -r file; do
  cmp -- "$file" "$restore_dir/$file"
done < <(tar -tzf "$archive")
```

The script keeps the newest seven matching archives by default. Verify
retention safely in an isolated temporary directory:

```bash
retention_test_dir="$(mktemp -d)"
touch "$retention_test_dir"/agent-test-20000101T00000{0,1,2}Z.tar.gz
BACKUP_DIR="$retention_test_dir" BACKUP_RETENTION_COUNT=2 ./scripts/backup.sh
find "$retention_test_dir" -maxdepth 1 -type f -name 'agent-test-*.tar.gz' -print | sort
```
