#!/bin/bash

##############################################################################
#
# This script will return 0 if the underlying application process is
# started.  This is primarily intended for use in environments that
# provide an application startup probe, in particular the Kubernetes
# `startupProbe` hook. See https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
# for more information.
#
##############################################################################

# The Bamboo agent uses a wrapper process to start and restart it on
# failure. The wrapper generates status files for it and the
# underlying application, so we can use this. See
# https://wrapper.tanukisoftware.com/doc/english/prop-statusfile.html,
# https://wrapper.tanukisoftware.com/doc/english/prop-java-statusfile.html
# and `bamboo-agent.sh` for details.
#
# The logic here is wait for the wrapper and agent to be started, then
# wait for the agent to be fully available. After this
# `probe-readiness.sh` should be used to monitor ongoing availability.

. /probe-common.sh

grep -q STARTED ${WRAPPER_STATUSFILE} \
     && grep -q STARTED ${JAVA_STATUSFILE} \
     && grep -q "${LOG_TARGET}" ${AGENT_LOG}
