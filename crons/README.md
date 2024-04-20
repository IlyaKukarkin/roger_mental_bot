# Crons setup

## Basic description & files structure

1. Mood cron - ask users to rate their mood for today. Stored in the file `mood.ts`. Runs every hour
2. Rate cron - approve/block user submitted messages. Stored in the file `rate.ts`. Runs 2 times per 24 hours
3. Stata cron - calculates global user rates stats for the images. Stored in the file `stata.ts`. Runs 1 time per 24 hours
4. `db.ts` file with utils to connect to the Mongo DB

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
