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
