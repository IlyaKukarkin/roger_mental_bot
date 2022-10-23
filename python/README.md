## Setup python

First, make sure that python 3.10.8 is installed: [Link to install python](https://www.python.org/downloads/)

Install doppler - [Link](https://docs.doppler.com/docs/install-cli)

```bash
brew install dopplerhq/cli/doppler
```

Login in doppler

```bash
doppler login
```

Setup doppler environment -> choose dev

```bash
doppler setup
```

Activate venv from `python/roger` directory

```bash
source roger-venv/bin/activate
```

Install python dependencies

```bash
pip3 install -r requirements.txt
```

Run roger bot

```bash
doppler run -- python3 main.py
```

After development finished, stop environment

```bash
deactivate
```

## Load bots to server

Use sFTP connection to upload bots to server

Directory `/opt/`

Don't forget to install all packages from `requirements.txt`

To send job to background:

1. Run commant as usual - example `python3 main.py`
2. Press `cntr + z` to exit process
3. Send it to background with command `bg`

To see all running jobs use `jobs` command

And to stop job use `kill $1` with number from `jobs` command
