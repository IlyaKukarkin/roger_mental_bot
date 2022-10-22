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
