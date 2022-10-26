#!bin/bash

sudo docker pull ikukarkin/roger:roger
sudo docker pull ikukarkin/roger:jimmy

sudo docker stop roger
sudo docker stop jimmy

sudo docker system prune -f
sudo docker system prune -f

sudo docker run -d -e DOPPLER_TOKEN="dp.st.prd.jcF0VKUrH257mirbf7jxSzfcgClp84ccGCbCPTgeJNE" --name=roger ikukarkin/roger:roger
sudo docker run -d -e DOPPLER_TOKEN="dp.st.prd.jcF0VKUrH257mirbf7jxSzfcgClp84ccGCbCPTgeJNE" --name=jimmy ikukarkin/roger:jimmy