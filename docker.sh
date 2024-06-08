#!/bin/bash
trap "docker-compose down" SIGINT
docker-compose up
