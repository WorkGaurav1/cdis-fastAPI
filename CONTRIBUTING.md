# Contributing

This is a standalone FastAPI backend template, built as a name-for-name,
route-for-route parity implementation of the CDIS Node/Express backend
(a separate project). It is not exported or synced from anywhere — real
work happens directly in this repo.

## Before opening a PR

```bash
ruff check . && ruff format --check . && pyright src && pytest
```

`pytest` runs against SQLite by default (no external services needed).
To also run it against a real MySQL instance (`TEST_DB_BACKEND=mysql`,
what CI's `integration-test` job does), see the README's database setup
section. These are exactly the checks CI runs — green locally means
green in CI.

## Reporting a security issue

See [`SECURITY.md`](SECURITY.md).
