#!/bin/bash
trap "sudo docker-compose down" SIGINT
sudo docker-compose up
