#!/bin/bash -l
set -x

# this is a temporary solution that is in alignment with the existing PBC way of working - when using the new API, the capabilities would not be added, instead, we would pass properties via wrapper -> agent
source /bamboo-update-capability.sh "system.isolated.docker" $IMAGE_ID
source /bamboo-update-capability.sh "system.isolated.docker.for" $RESULT_ID

if [[ $KUBE_NUM_EXTRA_CONTAINERS -ne 0 ]]; then
    retries=0
    # 30 retries per minute times 20 minutes = loop 600 times
    # it's so high because of docker downloads of side containers.
    container_start_retry_count=600
    echo "Waiting for $KUBE_NUM_EXTRA_CONTAINERS side containers to start"
    containers_directory=/pbc/kube
    while true; do
        if [ $retries -eq $container_start_retry_count ]; then
            echo "Side containers failed to create file(s) in $containers_directory"
            ls -la $containers_directory
            break
        elif [ "$(find $containers_directory -type f| wc -l)" != "$KUBE_NUM_EXTRA_CONTAINERS" ]; then
            echo "No match, waiting some more"
            sleep 2
            let retries=retries+1
        else
            echo "all sidecontainers have started"
            break
        fi
    done
fi

if [ -f '/buildeng-custom/setup.sh' ]; then
    source /buildeng-custom/setup.sh
fi

exec "$@"
