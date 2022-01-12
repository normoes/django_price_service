#!/bin/bash

set -Eeuo pipefail

# The 'docker' environment is marked by the environment variable 'DOCKER_ENV'.
if [ -z "${DOCKER_ENV+x}" ]; then
    # If this is not the 'docker-compose' environment,
    # either use a pre-defined (system, virtualenv) 'pip-compile' by
    #  ./update_requirements.txt -s ./venv/bin/
    #  or
    #  ./update_requirements.txt -s ~/.local/bin/
    # or simply use the container's installation of `pip-compile`.
    system=""
    while getopts ":s:" opt; do
        case $opt in
          s) system="$OPTARG"
          ;;
        esac
    done
    if [ -n "$system" ]; then
        interpreter="$system"
    else
        interpreter=""
    fi
else
    # If this is the 'docker' environment,
    # expect 'pip-compile' to be known system-wide.
    interpreter=""
fi

if [ -n "$interpreter" ]; then
    echo "Using 'pip-compile' in: '$interpreter'."
else
    echo "Using: '$(command -V pip-compile | cut -d ' ' -f 3)'."
fi

# Prepend the compiled requirements file with the current date (UTC).
# Force same locale for every one.
current_date=$(LC_ALL=en_US.utf8 date --utc)

echo -e "\e[32mCompile service dependencies.\e[39m"
"$interpreter"pip-compile --upgrade --output-file requirements.txt --pip-args "--no-cache-dir" requirements.in
sed -i "1i# Compile date: $current_date" requirements.txt
if [ -f "./requirements.test.in"  ];then
    echo -e "\e[32mCompile service test dependencies.\e[39m"
    "$interpreter"pip-compile --upgrade --output-file requirements.test.txt --pip-args "--no-cache-dir" requirements.test.in
    sed -i "1i# Compile date: $current_date" requirements.test.txt
fi
echo -e "\e[32mDone.\e[39m"
