#!/bin/bash

set -Eeuo pipefail

service=""
while getopts ":f:s:" opt; do
    case $opt in
      f) force="$OPTARG"
      ;;
      s) service="$OPTARG"
      ;;
    esac
done

if [ -n "$service" ]; then
    echo "{\"process\": \"stop\", \"event\": \"stop_serivce\", \"service\": $service}"
    docker-compose -p price_service -f docker-compose.yml rm -sf "$service"
else
    echo '{"process": "run", "event": "run_serivce", "service": "all"}'
    docker-compose -p price_service -f docker-compose.yml rm -sf
fi
