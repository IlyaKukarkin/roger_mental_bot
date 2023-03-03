~~~~## Setup python

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

 ## Git flow

1. Locally pull changes from the `main` branch
2. Create a new branch from the `main` branch to add fix/feature
3. Make changes, push new bransh and create a pull request
4. Test everything on a test bots by running the bot locally. There are test tokens for both bots in doppler (TOKEN_BOT, TOKEN_VOLUNTEER_TEST_BOT)
5. If everything is ok, then raise the version in `roger/main.py` and `jimmy/handles/version` and merge in `main` branch
6. After 5 minutes check the version in the bot
 
 
 ## Load bots to server (OLD INFO, JUST FOR REFERENCE)

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
docker save roger:2410 > roger:2410.tar
```

4. Use sFTP connection as admin to upload bots to server to the directory `/opt/roger`

5. After transfer open server with `ssh` and login as admin `user`

6. Go to the directory with archive file `/opt/roger`

7. Load archive to docker on server
```bash
sudo docker load < roger:2410.tar
```

8. You can delete .tar archive from server to save space

9. Stop previus running container. Check what name it has with command
```bash
sudo docker container ls
```

10. Remember container name from previeus step and stop this container. For example, if the name was roger
```bash
sudo docker stop roger
```

11. Run new image with this docker command with token from Doppler (without "$" symbol)
```bash
sudo docker run --name roger -d -e DOPPLER_TOKEN="$DOPPLER_TOKEN" roger:2410
```

12. If everything working good, we can delete old images and containsers. Remove all stopped containers
```bash
sudo docker rm $(sudo docker ps --filter status=exited -q)
```

13. And remove all unused images
```bash
sudo docker images prune -a
```

All same for other bot -> Jimmy. Just different name