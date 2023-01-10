#!/bin/bash -l
set -x

if [ -f '/var/run/secrets/kubernetes.io/serviceaccount/namespace' ]; then
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

exec "$@"
