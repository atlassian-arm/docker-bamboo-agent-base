ARG BASE_IMAGE=eclipse-temurin:11
FROM $BASE_IMAGE

LABEL maintainer="dc-deployments@atlassian.com"
LABEL securitytxt="https://www.atlassian.com/.well-known/security.txt"

ENV APP_NAME                                bamboo_agent
ENV RUN_USER                                bamboo
ENV RUN_GROUP                               bamboo
ENV RUN_UID                                 2005
ENV RUN_GID                                 2005

ENV BAMBOO_AGENT_HOME                       /var/atlassian/application-data/bamboo-agent
ENV BAMBOO_AGENT_INSTALL_DIR                /opt/atlassian/bamboo
ENV KUBE_NUM_EXTRA_CONTAINERS               0
ENV EXTRA_CONTAINERS_REGISTRATION_DIRECTORY /pbc/kube
ENV DISABLE_AGENT_AUTO_CAPABILITY_DETECTION false

WORKDIR $BAMBOO_AGENT_HOME

CMD ["/usr/bin/tini", "--", "/entrypoint.py"]
ENTRYPOINT ["/pre-launch.sh"]

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
         git git-lfs \
         openssh-client \
         python3 python3-jinja2 python-is-python3 \
         tini \
    && apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ARG MAVEN_VERSION=3.6.3
ENV MAVEN_HOME                              /opt/maven
RUN mkdir -p ${MAVEN_HOME} \
    && curl -L --silent https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz | tar -xz --strip-components=1 -C "${MAVEN_HOME}" \
    && ln -s ${MAVEN_HOME}/bin/mvn /usr/local/bin/mvn

ARG BAMBOO_VERSION
ARG DOWNLOAD_URL=https://packages.atlassian.com/mvn/maven-atlassian-external/com/atlassian/bamboo/atlassian-bamboo-agent-installer/${BAMBOO_VERSION}/atlassian-bamboo-agent-installer-${BAMBOO_VERSION}.jar

COPY bamboo-update-capability.sh /
RUN groupadd --gid ${RUN_GID} ${RUN_GROUP} \
    && useradd --uid ${RUN_UID} --gid ${RUN_GID} --home-dir ${BAMBOO_AGENT_HOME} --shell /bin/bash ${RUN_USER} \
    && echo PATH=$PATH > /etc/environment \
    \
    && mkdir -p                             ${BAMBOO_AGENT_INSTALL_DIR} \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_AGENT_INSTALL_DIR} \
    && curl -L --silent                     ${DOWNLOAD_URL} -o "${BAMBOO_AGENT_INSTALL_DIR}/atlassian-bamboo-agent-installer.jar" \
    && mkdir -p                             ${BAMBOO_AGENT_HOME}/conf ${BAMBOO_AGENT_HOME}/bin \
    \
    && /bamboo-update-capability.sh "system.jdk.JDK 1.11" ${JAVA_HOME}/bin/java \
    && /bamboo-update-capability.sh "JDK 11" ${JAVA_HOME}/bin/java \
    && /bamboo-update-capability.sh "Python" /usr/bin/python3 \
    && /bamboo-update-capability.sh "Python 3" /usr/bin/python3 \
    && /bamboo-update-capability.sh "Git" /usr/bin/git \
    \
    && chown -R ${RUN_USER}:${RUN_GROUP} ${BAMBOO_AGENT_HOME}

COPY entrypoint.py \
     probe-common.sh \
     probe-startup.sh \
     probe-readiness.sh \
     pre-launch.sh \
     shared-components/image/entrypoint_helpers.py  /
COPY shared-components/support                      /opt/atlassian/support
COPY config/*                                       /opt/atlassian/etc/
