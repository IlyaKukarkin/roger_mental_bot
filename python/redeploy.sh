#!bin/bash

sudo docker pull ikukarkin/roger:roger
sudo docker pull ikukarkin/roger:jimmy

sudo docker stop roger
sudo docker stop jimmy

sudo docker system prune -f

sudo docker run -d -e DOPPLER_TOKEN=$1 --name=roger ikukarkin/roger:roger
sudo docker run -d -e DOPPLER_TOKEN=$1 --name=jimmy ikukarkin/roger:jimmy