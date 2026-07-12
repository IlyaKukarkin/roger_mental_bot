# Crons setup

## Basic description & files structure

1. Mood cron - ask users to rate their mood for today. Stored in the file `mood.ts`. Runs every hour
2. Rate cron - approve/block user submitted messages. Stored in the file `rate.ts`. Runs 2 times per 24 hours
3. Stata cron - calculates global user rates stats for the images. Stored in the file `stata.ts`. Runs 1 time per 24 hours
4. `db.ts` file with utils to connect to the Mongo DB
5. Backup cron - dumps the whole MongoDB, encrypts the dump and uploads it to a Cloudflare R2 bucket. Lives on the shared OVH host (`/opt/mongo-backup.sh`), not in this repo. Runs 1 time per 24 hours

## Database backup cron

The production backup does NOT run from this repo. It lives on the shared
OVH host (the one also running vpnbot): root crontab runs
`/opt/mongo-backup.sh` daily at 02:00 UTC, logging to
`/opt/backups/mongodump-cron.log`. The script streams
`mongodump → age (encryption) → aws s3 cp` without touching the disk and
backs up both projects: roger (bucket `roger`) and vpnbot (bucket `vpnbot`),
under the `mongodump/` prefix.

Secrets:

- R2 credentials and `MONGODB_URI` come from the `prd` Doppler config of
  `roger-mental-bot` (service token in `/opt/.env` on the host)
- the age key pair lives in the `server-configs` Doppler project (`prd`):
  `BACKUP_AGE_RECIPIENT` (public) / `BACKUP_AGE_PRIVATE_KEY` (private);
  the private key is also in `/opt/BACKUP_AGE_KEYS.txt` on the host (root, 600)

Retention is handled by R2 itself: an object lifecycle rule on the bucket
(Dashboard → R2 → bucket → Settings → Object lifecycle rules) deletes old
objects.

To restore a backup:

```bash
age -d -i key.txt roger-<timestamp>.archive.gz.age | mongorestore --archive --gzip --uri="$MONGODB_URI"
```

There is also a standalone `crons/backup.sh` in this repo — a self-contained
variant of the same dump-encrypt-upload flow (file-based, with healthchecks
pings) that can be run manually from any machine with
`mongodb-database-tools`, `awscli`, `curl` and `age` installed:

```bash
doppler run --config prd -- bash crons/backup.sh
```

## Requirements

To run crons VPS must have installed these packages _globally_

- [Bun](https://bun.sh/)
- [Doppler](https://www.doppler.com)
- [MongoDB](https://www.npmjs.com/package/mongodb)
- [Logtail](https://www.npmjs.com/package/@logtail/next)

## Monitoring

We are using [Healthchecks](https://healthchecks.io/projects/c0d78736-0ff1-4d59-83e8-0c6421f63ba7/checks/) service to log and notify if the crons are not running smoothly

Each cron has a ping API call to the Healthchecks service after main code excecution

## Problems

- Right now there is a lot of duplicated code, as "crons" folder has to work as a standalone application on the VPS and we don't have a lot of time to come up with a good approach. Possible solutons:
  - Move code to the crons folder and use it from there in application <- not the best approach as we are losing good file structure
  - Rool-out FE application on the VPS and then crons should just ping the API endpoint and it's all good <- this approach is the best, as we will be able to atoumate code rollouts on master branch merges and there will be no code duplication
