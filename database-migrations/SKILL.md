---
name: database-migrations
description: Use when writing or running production schema migrations (expand/contract, online DDL, backfills, ORM migrators) or pairing a breaking schema change with a code deploy.
---
# Database Migrations

A migration is code that runs against a live database. It can **lock tables for hours, corrupt data, or hang replication** if written carelessly. The canonical safe pattern is **expand / contract**:

```
EXPAND   → add new structure; old + new code both work
MIGRATE  → deploy new code; dual-read / dual-write
BACKFILL → copy existing data into the new shape, throttled
CUTOVER  → point everything at the new structure
CONTRACT → remove the old structure
```

Each step is independently deployable and **reversible without a data restore**. Never combine expand + cutover + contract in one change.

This skill focuses on **online** migrations — zero or near-zero downtime against production. Dev-only migrations are easier; they can be collapsed into a single file.

## When to use

- Writing a migration file.
- Reviewing a PR that includes schema changes.
- Planning a schema change on a table above ~100k rows.
- Operating or rolling back a migration that caused lock contention, replication lag, or runtime errors.
- Deleting / masking PII under GDPR / LGPD / regulatory rules.

### When NOT to use (simplified path)

- Fresh database, no traffic, dev only → single migration file, no contract phase.
- Toy table under ~10k rows, non-critical → one-shot DDL is fine, but still follow naming / reversibility rules.
- Read-only report databases → DDL can be simpler, but still use lock timeouts.

## Before writing the migration

Answer these **before** opening the tool:

1. **How big is the target table?** Rows, size on disk, row width. A migration that runs in 3s on 10k rows can run 6h on 10M rows.
2. **Is the table hot?** Read/write rate at peak. Hot tables cannot tolerate `AccessExclusive` locks for even a second.
3. **What is the replication topology?** Primary + replicas, logical replication, CDC, foreign data wrappers. Some DDL breaks CDC.
4. **What is the data-loss risk?** A drop-column is irreversible. A rename is reversible. A type narrowing is irreversible for out-of-range values.
5. **Is there a backup / PITR checkpoint?** Verify — do not assume.
6. **Can the change be expand/contract?** 95% can. Know why when it cannot.

## The expand / contract pattern in detail

### 1. EXPAND — additive only

```sql
-- Add a new column, NULLable, no default; safe on large tables.
ALTER TABLE users ADD COLUMN email_normalized TEXT;

-- Add an index without blocking writes (Postgres).
CREATE INDEX CONCURRENTLY idx_users_email_normalized
  ON users (email_normalized)
  WHERE email_normalized IS NOT NULL;
```

Rules:
- New structure must be **NULLable** or have a constant default (constant, *not* a function like `NOW()`, which locks on MySQL / old Postgres).
- New indexes with `CONCURRENTLY` (Postgres) or `ALGORITHM=INPLACE, LOCK=NONE` (MySQL 5.6+).
- New constraints with `NOT VALID` first, `VALIDATE` later (Postgres):
  ```sql
  ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id)
    REFERENCES users(id) NOT VALID;
  -- Later, when traffic allows:
  ALTER TABLE orders VALIDATE CONSTRAINT fk_user;
  ```
- **Do not** use `NOT NULL` or `DEFAULT <expensive>` on new columns against a big table. Add NULLable, backfill, then add NOT NULL with a validation step.

### 2. MIGRATE — dual code

Deploy application code that:
- **Writes to both** old and new column (or new table).
- **Reads new**, falling back to old when new is NULL (for migrated rows).
- Treats old as the source of truth for correctness until cutover.

This step is pure application deploy — see [`deploy-safety`](../deploy-safety) + [`incremental-implementation`](../incremental-implementation).

Only after this deploy is stable do you run the backfill.

### 3. BACKFILL — slow, safe, resumable

```sql
-- Idiomatic Postgres pattern: loop small batches with a throttle.
-- Run from a one-off job, not from the app startup path.
DO $$
DECLARE
  batch_size  INT := 5000;
  updated    INT;
BEGIN
  LOOP
    UPDATE users
       SET email_normalized = lower(trim(email))
     WHERE id IN (
       SELECT id FROM users
        WHERE email_normalized IS NULL
        LIMIT batch_size
        FOR UPDATE SKIP LOCKED
     );
    GET DIAGNOSTICS updated = ROW_COUNT;
    EXIT WHEN updated = 0;
    PERFORM pg_sleep(0.2);           -- throttle
    RAISE NOTICE 'batch committed: %', updated;
    COMMIT;
  END LOOP;
END $$;
```

Rules:
- **Small batches** (1k-10k rows). Big `UPDATE`s bloat WAL / binlog and block replication.
- **Throttle** with `pg_sleep` / `SLEEP()`. Consume less than 25% of the primary's capacity.
- **Resumable.** `WHERE email_normalized IS NULL` lets you stop and continue.
- **Idempotent.** Running the backfill twice must not corrupt data.
- **Monitor replication lag** during backfill. If lag grows, throttle harder or pause.
- **Run from a dedicated job** (K8s Job, GitHub Actions, a runbook step) — not from the app at startup.

For huge tables or MySQL without row-level `SKIP LOCKED` tricks, use:
- [`pt-online-schema-change`](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html) (Percona) — builds a shadow table via triggers, then swaps.
- [`gh-ost`](https://github.com/github/gh-ost) (GitHub) — trigger-less; uses binlog replay.
- [Atlas](https://atlasgo.io/) — schema-as-code with migration planning.

### 4. CUTOVER

The application now reads and writes **only** from the new column / table. Old structure remains in place but is unused.

- Deploy new code.
- Observe for a full bake window (see [`deploy-safety`](../deploy-safety) — minutes to hours depending on risk).
- Keep the old structure for at least one more deploy cycle.

### 5. CONTRACT

Remove the old column / table.

```sql
-- Final step after bake. Reversible only by restoring the column + backfill.
ALTER TABLE users DROP COLUMN email;
```

- Do not contract on the same day you cut over. Give yourself a rollback window.
- Before drop: confirm **no code paths** reference the old column (grep + metrics on query shapes if your DB offers them).
- If a drop is irreversible and worries you, `ALTER TABLE ... RENAME COLUMN email TO email_deprecated_20250601` first. Drop a month later. Cheap safety.

## Locks and lock timeouts

The #1 cause of "the migration took down prod" is a DDL that took an `AccessExclusive` lock and blocked reads.

### Always set a lock timeout

```sql
-- Postgres
SET lock_timeout = '3s';
ALTER TABLE orders ADD COLUMN notes TEXT;      -- if lock not acquired in 3s, fails fast
```

```sql
-- MySQL
SET SESSION lock_wait_timeout = 3;
ALTER TABLE orders ADD COLUMN notes TEXT;
```

If the migration framework supports it, set a global timeout for every migration. The alternative — DDL hanging behind a long `SELECT FOR UPDATE` — can cascade into a full outage as every new query queues behind the DDL waiting for the lock.

### Know the lock levels

| Operation (Postgres) | Lock level | Safe on hot table? |
|---------------------|-----------|---------------------|
| `ADD COLUMN NULL no default` | `AccessExclusive`, brief | Yes (modern PG) |
| `ADD COLUMN NOT NULL DEFAULT const` (PG 11+) | `AccessExclusive`, brief | Yes (modern PG) |
| `ADD COLUMN NOT NULL` without default | Full rewrite, long lock | **No** |
| `ALTER COLUMN ... SET NOT NULL` | Full table scan | **No** — use `ADD CONSTRAINT CHECK ... NOT VALID` + `VALIDATE` |
| `ALTER COLUMN ... TYPE` (narrowing / changing) | Full rewrite | **No** |
| `CREATE INDEX` (without `CONCURRENTLY`) | Blocks writes | **No** — always `CONCURRENTLY` |
| `CREATE INDEX CONCURRENTLY` | Non-blocking | Yes, but slower |
| `DROP INDEX` | Brief exclusive | OK, usually fast |
| `ADD FOREIGN KEY` | Scan + lock | **No** — use `NOT VALID` + `VALIDATE` |
| `RENAME TABLE/COLUMN` | Brief exclusive | OK, usually fast |

MySQL / InnoDB has analogous classifications. Check per version and per engine (pt-osc / gh-ost work around the worst cases).

### Retry logic

If the lock timeout fails, the migration framework should retry (with backoff) and ultimately surface a clear error. Do **not** retry indefinitely — that hides a blocker.

## Transactional DDL

Postgres wraps DDL in a transaction by default, which is a gift: if one statement fails, nothing applied. Use it.

```sql
BEGIN;
ALTER TABLE users ADD COLUMN email_normalized TEXT;
ALTER TABLE users ADD COLUMN phone_normalized TEXT;
COMMIT;
```

**Exceptions**: `CREATE INDEX CONCURRENTLY` cannot run inside a transaction. Run it separately.

MySQL 5.7 has implicit commit on DDL — every `ALTER` is its own commit. Cannot batch multi-statement atomicity. Migration frameworks handle this by tracking per-statement state.

## Migration file conventions

Most frameworks give you `up` and `down`. Write `down` even when it "cannot really reverse" — at minimum, document why:

```sql
-- migrations/20250601120000_expand_email_normalized.sql

-- UP
SET lock_timeout = '3s';
ALTER TABLE users ADD COLUMN email_normalized TEXT;
CREATE INDEX CONCURRENTLY idx_users_email_normalized
  ON users (email_normalized)
  WHERE email_normalized IS NOT NULL;

-- DOWN
-- Safe to reverse: column is additive, index is independent.
SET lock_timeout = '3s';
DROP INDEX IF EXISTS idx_users_email_normalized;
ALTER TABLE users DROP COLUMN IF EXISTS email_normalized;
```

### Naming

`YYYYMMDDHHMMSS_verb_what.sql`:

```
20250601120000_expand_email_normalized.sql
20250601120500_backfill_email_normalized.sql
20250608090000_cutover_read_email_normalized.sql
20250615090000_contract_drop_email.sql
```

Each file is small, single-purpose, reviewable.

### Review checklist for a migration PR

- [ ] Lock timeout is set.
- [ ] No `NOT NULL` / expensive default on `ADD COLUMN` without a backfill step.
- [ ] `CREATE INDEX` uses `CONCURRENTLY` (Postgres) / appropriate online DDL (MySQL).
- [ ] Constraints added with `NOT VALID` + later `VALIDATE` when on hot tables.
- [ ] `DROP` of anything is guarded by a deprecation / rename-first step.
- [ ] `down` exists or is explicitly `-- irreversible: <reason>`.
- [ ] Backfill is batched, throttled, resumable, idempotent.
- [ ] Migration is in its own commit, separate from the app change (see [`incremental-implementation`](../incremental-implementation)).

## Testing migrations

Do not test migrations only against an empty dev DB. Minimum:

- Run against a **prod-size snapshot** of the database in a staging environment.
- Measure **duration** and **lock duration** explicitly.
- For backfills, verify throughput, resume behavior, and replication lag.
- Rehearse the rollback.

Tools:
- [Atlas](https://atlasgo.io/) — schema diff, migration plan, lint rules for destructive DDL.
- [`squawk`](https://github.com/sbdchd/squawk) — Postgres migration linter (catches missing `CONCURRENTLY`, locking `NOT NULL`, etc.).
- [`ghost`](https://github.com/github/gh-ost) / [`pt-online-schema-change`](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html) — the tools themselves dry-run against the target.

## Framework-specific notes

### Postgres + Alembic

- `op.add_column('users', Column('email_norm', Text))` — fine.
- `op.create_index('idx_users_email_norm', 'users', ['email_norm'], postgresql_concurrently=True)` — **set `@migration.run_concurrently()`** or Alembic wraps it in a transaction and fails.
- For mixed transactional + non-transactional DDL, split into two migrations.

### Rails / ActiveRecord

- `add_column :users, :email_norm, :text, null: true` — fine.
- `add_index :users, :email_norm, algorithm: :concurrently` — set `disable_ddl_transaction!` at the top of the migration.
- Use the [`strong_migrations`](https://github.com/ankane/strong_migrations) gem to lint destructive migrations at CI time.

### Prisma Migrate

- Prisma generates SQL but does not know about online DDL. Audit generated files; rewrite when needed.
- `prisma migrate deploy` runs pending migrations in order; wrap in a K8s Job for production.

### golang-migrate

- Plain SQL files; full control. Use separate files for transactional and non-transactional steps.
- `migrate -path ./migrations -database $DATABASE_URL up 1` applies exactly one.

### Liquibase / Flyway

- Rich plugin ecosystems for many DBs. For destructive changes, Flyway's `repair` / Liquibase's `rollback` must be tested before relying on them.

## Rollback playbook

Every migration PR includes the rollback in the description:

```
Rollback plan:
  1. Revert application deploy to <previous SHA>.
  2. Run migration down:
        migrate -path ./migrations -database $DATABASE_URL down 1
  3. If backfill already ran: NO automatic rollback.
     Old column is still present; new code ignores new column.
     No data corruption.
```

If the rollback is "restore from PITR + redeploy", that is a red flag — the migration was not expand/contract.

## When the migration is already running wrong

This becomes an [incident-response](../incident-response) event.

Triage:
1. **Is it locking production?** `pg_stat_activity` (Postgres) / `SHOW PROCESSLIST` (MySQL) — find long-running DDL.
2. **Is it safe to kill?** If inside a transaction, `SELECT pg_cancel_backend(<pid>)` rolls back cleanly. For non-transactional DDL, the DB will handle state (with caveats).
3. **Is replica lag out of control?** Pause the migration, let replicas catch up, resume with smaller batches.
4. **Communicate**. This is an incident if users are hit.

Never try to "fix" a mid-flight migration with another DDL on top. Roll back, regroup, re-plan.

## PII and regulatory deletions

Deletion under GDPR / LGPD / CCPA often runs as a migration-shaped job. Rules:

- **Soft-delete first, hard-delete later.** Soft-delete is reversible within a grace period; hard-delete is not.
- **Mask instead of delete** when the foreign-key graph matters. Replace PII fields with constants (`'deleted-user-123'`) so referential integrity holds.
- **Log the deletion**, including requestor, timestamp, and the ID of the record. Audit trail is required in most regimes.
- **Backfill old partitions / backups**. A deletion that leaves PII in yesterday's snapshot is not a deletion.
- **Scope and throttle.** A million-row delete can take down replication. Batch it like any backfill.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| `ALTER TABLE ... ADD COLUMN NOT NULL DEFAULT now()` on large table | Full rewrite under `AccessExclusive` lock |
| `CREATE INDEX` without `CONCURRENTLY` | Writes block for the duration of the scan |
| `ALTER COLUMN ... TYPE` to narrow (e.g. TEXT → VARCHAR(100)) | Full rewrite; any row over the limit aborts |
| Adding FK on a hot table without `NOT VALID` | Full scan under lock |
| Backfill as one big `UPDATE` | WAL bloat, replica lag, lock contention |
| Backfill run from application startup | App unhealthy = migration pending = deploy stuck |
| Migration + new code in one deploy | No rollback story — code refers to columns that don't exist yet |
| `DROP` on the same PR as cutover | Removes the escape hatch |
| Dev-only migrations committed straight to prod | Dev schemas differ; staging should mirror prod |
| No lock timeout | DDL hangs behind a long read; cascade failure |
| Migration runs from a developer laptop | Kill the laptop, DB is half-migrated |
| `DELETE FROM users WHERE ...` for GDPR without batching | Locks, replica lag, missed backups |
| No rehearsal against prod-size data | "It ran in 3s locally" is not a measurement |

## Interaction with other skills

- [`deploy-safety`](../deploy-safety) — migrations are part of a deploy. Feature flags + expand/contract + canary = zero-downtime schema change.
- [`incident-response`](../incident-response) — when a migration breaks prod, this is your playbook.
- [`incremental-implementation`](../incremental-implementation) — expand → migrate → backfill → cutover → contract is five slices, not one.
- [`code-review`](../code-review) — migration PRs get a dedicated axis: locking risk, reversibility, backfill shape.
- [`observability`](../observability) — replica lag, lock wait time, slow queries are signals during a migration.
- [`runbook-authoring`](../runbook-authoring) — runbook for each migration class (backfill, large-index, PII-deletion).
- [`architecture-decision-records`](../architecture-decision-records) — non-trivial schema changes (multi-tenant partitioning, event sourcing, etc.) warrant an ADR.
- [`security-hardening`](../security-hardening) — PII deletion / masking; audit log of the deletion itself.

## Verification checklist

Before merging a migration PR:

- [ ] Lock timeout is set.
- [ ] No destructive DDL on a hot table without a workaround (`CONCURRENTLY`, `NOT VALID`, expand/contract).
- [ ] Backfill batched, throttled, resumable, idempotent.
- [ ] `down` migration exists or is marked irreversible with rationale.
- [ ] Expand / migrate / backfill / cutover / contract split into separate PRs when the change is non-trivial.
- [ ] Tested against a prod-size dataset; duration measured.
- [ ] Rollback plan in the PR description.
- [ ] Runbook updated if this class of migration is recurring.
- [ ] Observability alerts tuned: replica lag, lock wait, migration duration.

Before running in production:

- [ ] Backup / PITR checkpoint verified fresh.
- [ ] Maintenance window (if any) agreed.
- [ ] On-call notified.
- [ ] Replication lag is low and stable.
- [ ] Migration is running from a controlled job (K8s Job / CI job), not a developer machine.
