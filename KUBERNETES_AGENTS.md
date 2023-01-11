##How to run locally:
1. `docker build --build-arg BAMBOO_VERSION=9.1.0 -f Dockerfile.kubernetes --tag kubernetes-agent-image . `
2. ` docker run -e BAMBOO_SERVER=http://YOUR_IP:6990/bamboo/agentServer/ -e SECURITY_TOKEN=YOUR_TOKEN -e KUBE_NUM_EXTRA_CONTAINERS=0 -e IMAGE_ID=kubernetes-agent-image -e RESULT_ID=SOME_RESULT_ID --name="bambooAgent" --hostname="bambooAgent" kubernetes-agent-image`