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

After adding new packages, you should update requirements.txt file
```bash
pip freeze > requirements.txt
```

 ## Load bots to server

!! You should have docker installed and running on your machine. [Link](https://docs.docker.com/desktop/install/mac-install/)

1. Open terminal and navigate to folder with bot
```bash
cd python/roger
```

2. Create docker image with command 
```bash
docker build -t roger:2410 .
```
Numbers after symbol ":" mean "tag name" and can be used to put current date

3. Save created image to archive with command 
```bash
docker save roger > roger.tar
```

4. Use sFTP connection to upload bots to server to the directory `/opt/roger`

5. After transfer open server with `ssh` and login as root `user`

6. Go to the directory with archive file `/opt/roger`

7. Load archive to docker on server
```bash
sudo docker load < roger.tar
```

8. Run image with this docker command with token from Doppler (without "$" symbol)
```bash
sudo docker run -d -e DOPPLER_TOKEN="$DOPPLER_TOKEN" roger
```

All same for other bot -> Jimmy. Just different name