#!/bin/sh

# delete the exiting image if it exists
docker rmi -f voiceprint

# build a new image
docker build -t voiceprint .

#run the application
docker run -p 5000:5000 voiceprint
