#!/bin/bash

set -Eeo pipefail

cd /code

exec gosu "$USER_NAME" "$@"
