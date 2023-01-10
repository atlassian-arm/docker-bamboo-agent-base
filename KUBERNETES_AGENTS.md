##How to run:
1. `docker build --build-arg BAMBOO_VERSION=9.1.0 --tag kubernetes-agent-image . `
2. `docker run -e BAMBOO_SERVER=http://YOUR_IP:6990/bamboo/agentServer/ -e SECURITY_TOKEN=YOUR_TOKEN -e KUBE_NUM_EXTRA_CONTAINERS=XYZ -v bambooVolume:/var/atlassian/application-data/bamboo --name="bambooAgent" --hostname="bambooAgent" kubernetes-agent-image`