#!/bin/bash

set -Eeuo pipefail

function clean_up {
    echo '{"process": "test", "event": "general_cleanup"}'
    docker-compose -p price_service_test -f docker-compose-testing.yml rm -s -f
}

trap 'clean_up; exit 0' 0

force=""
single=""
while getopts ":f:k:" opt; do
    case $opt in
      f) force="$OPTARG"
      ;;
      k) single="$OPTARG"
      ;;
    esac
done

docker-compose -p price_service_test -f docker-compose-testing.yml rm -s -f

if [ -n "$force" ]; then
    echo '{"process": "build", "event": "build_serivce_no_cache", "scope": "all"}'
    docker-compose -p price_service_test -f docker-compose-testing.yml build --no-cache
else
    docker-compose -p price_service_test -f docker-compose-testing.yml build
fi

if [ -n "$single" ]; then
    echo "{\"process\": \"test\", \"event\": \"test_serivce\", \"scope\": \"$single\"}"
    docker-compose -p price_service_test -f docker-compose-testing.yml run --rm test tox -e py38 -- -k "$single"

else
    echo '{"process": "test", "event": "test_serivce", "scope": "all"}'
    docker-compose -p price_service_test -f docker-compose-testing.yml run --rm test tox -e py38
fi

docker-compose -p price_service_test -f docker-compose-testing.yml logs -f
