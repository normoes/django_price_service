#!/bin/bash

set -Eeuo pipefail

function clean_up {
    echo '{"process": "run", "event": "error_cleanup"}'
    docker-compose -p price_service -f docker-compose.yml rm -s -f
}

trap 'clean_up; exit 0' EXIT

force=""
update=""
migration=""
init=""
while getopts ":f:u:m:i:" opt; do
    case $opt in
      f) force="$OPTARG"
      ;;
      u) update="$OPTARG"
      ;;
      m) migration="$OPTARG"
      ;;
      i) init="$OPTARG"
      ;;
    esac
done

if [ -n "$force" ]; then
    echo '{"process": "build", "event": "build_service_no_cache", "scope": "all"}'
    docker-compose -p price_service -f docker-compose.yml build --no-cache
fi

echo '{"process": "maintenance", "event": "remove_running", "scope": "all"}'
docker-compose -p price_service -f docker-compose.yml rm -s -f

if [ -n "$update" ]; then
    echo '{"process": "maintenance", "event": "update_dependencies", "scope": "all"}'
    docker-compose -p price_service -f docker-compose.yml build update
    docker-compose -p price_service -f docker-compose.yml run --rm update ./update_requirements.sh
else
    if [ -n "$init" ]; then
        echo '{"process": "init", "event": "init_environment", "scope": "all"}'
        docker-compose -p price_service -f docker-compose.yml up -d postgres rabbitmq
        sleep 5
        # Create Django super user.
        docker-compose -p price_service -f docker-compose.yml build service
        docker-compose -p price_service -f docker-compose.yml run --rm --entrypoint "" -u $(id -u) service bash -c "cd /code && python manage.py createsuperuser"
        sleep 5
        # Create additional vhostin rabbitmq.
        docker-compose -p price_service -f docker-compose.yml exec rabbitmq bash -c 'rabbitmqctl add_vhost price_service && rabbitmqctl set_permissions -p price_service user ".*" ".*" ".*"'

    elif [ -n "$migration" ]; then
        echo '{"process": "maintenance", "event": "makemigrations", "scope": "all"}'
        docker-compose -p price_service -f docker-compose.yml up -d postgres
        sleep 5
        docker-compose -p price_service -f docker-compose.yml build service
        docker-compose -p price_service -f docker-compose.yml run --rm --entrypoint "" -u $(id -u) service bash -c "cd /code && python manage.py makemigrations --name $migration"
    else
        echo '{"process": "run", "event": "run_service", "scope": "all"}'
        docker-compose -p price_service -f docker-compose.yml up -d postgres rabbitmq
        sleep 5
        docker-compose -p price_service -f docker-compose.yml build service  celery_worker celery_beat
        docker-compose -p price_service -f docker-compose.yml run --rm --entrypoint "" -u $(id -u) service bash -c "python manage.py migrate"
        docker-compose -p price_service -f docker-compose.yml run --rm -d --entrypoint "" -u $(id -u) celery_worker celery -A price_service worker --loglevel=INFO -f /tmp/celery_worker.log
        docker-compose -p price_service -f docker-compose.yml up -d celery_beat
        docker-compose -p price_service -f docker-compose.yml run --rm --service-ports --entrypoint "" -u $(id -u) service bash -c "python manage.py runserver 0.0.0.0:8080"
    fi
fi
