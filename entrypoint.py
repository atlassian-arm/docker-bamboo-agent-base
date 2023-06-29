#!/usr/bin/python3

import os
import sys

from entrypoint_helpers import env, gen_cfg, logging, set_perms, str2bool, exec_app

RUN_USER = env['run_user']
RUN_GROUP = env['run_group']
BAMBOO_AGENT_HOME = env['bamboo_agent_home']
BAMBOO_AGENT_INSTALL_DIR = env['bamboo_agent_install_dir']

DOCKER_SOCK = '/var/run/docker.sock'

BAMBOO_EPHEMERAL_AGENT_DATA_KEY = 'bamboo_ephemeral_agent_data'
BAMBOO_EPHEMERAL_AGENT_DATA = env.get(BAMBOO_EPHEMERAL_AGENT_DATA_KEY)
BAMBOO_EPHEMERAL_AGENT_DATA_MAP = {}
if BAMBOO_EPHEMERAL_AGENT_DATA:
    BAMBOO_EPHEMERAL_AGENT_DATA_MAP = {env.split("=")[0]: env.split("=")[1] for env in BAMBOO_EPHEMERAL_AGENT_DATA.split("#")}


BAMBOO_SERVER_KEY = 'bamboo_server'
BAMBOO_SERVER = env.get(BAMBOO_SERVER_KEY) if env.get(BAMBOO_SERVER_KEY) else BAMBOO_EPHEMERAL_AGENT_DATA_MAP.get(BAMBOO_SERVER_KEY)
env[BAMBOO_SERVER_KEY] = BAMBOO_SERVER
BAMBOO_EPHEMERAL_AGENT_DATA_MAP.pop(BAMBOO_SERVER_KEY, None)

if not BAMBOO_SERVER:
    logging.error('No value for "BAMBOO_SERVER" found in the environment. Shutting down.')
    sys.exit(1)

BAMBOO_SERVER = BAMBOO_SERVER.rstrip('/')
if not BAMBOO_SERVER.endswith('/agentServer'):
    BAMBOO_SERVER += '/agentServer'
    env[BAMBOO_SERVER_KEY] = BAMBOO_SERVER

SECURITY_TOKEN_KEY = "security_token"
SECURITY_TOKEN = env.get(SECURITY_TOKEN_KEY) if env.get(SECURITY_TOKEN_KEY) else BAMBOO_EPHEMERAL_AGENT_DATA_MAP.get(SECURITY_TOKEN_KEY)
env[SECURITY_TOKEN_KEY] = SECURITY_TOKEN
BAMBOO_EPHEMERAL_AGENT_DATA_MAP.pop(SECURITY_TOKEN_KEY, None)

#setting remaining environment variables
ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES = ""
for key, value in BAMBOO_EPHEMERAL_AGENT_DATA_MAP.items():
    if ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES:
        ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES = ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES + '#'
    ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES = ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES + key + '=' + value

if ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES:
    env[BAMBOO_EPHEMERAL_AGENT_DATA_KEY] = ACCUMULATED_REMAINING_ENVIRONMENT_VARIABLES

gen_cfg('wrapper.conf.j2', f'{BAMBOO_AGENT_HOME}/conf/wrapper.conf',
        user=RUN_USER, group=RUN_GROUP, overwrite=False)

# Although Docker is not installed in this base image, there's no easy way for an image
# derived from this base to perform this particular step, which must be run at container
# start rather than at build time.
if os.path.exists(DOCKER_SOCK):
    set_perms(DOCKER_SOCK, 'root', 'root', 0o666)

JAVA_OPTS = f'-Dbamboo.home={BAMBOO_AGENT_HOME}'

AGENT_OPTS = [f'{BAMBOO_SERVER}']
if SECURITY_TOKEN:
    AGENT_OPTS.extend(['-t', f'{SECURITY_TOKEN}'])

exec_app(['/opt/java/openjdk/bin/java', JAVA_OPTS, '-jar', f'{BAMBOO_AGENT_INSTALL_DIR}/atlassian-bamboo-agent-installer.jar'] + AGENT_OPTS, BAMBOO_AGENT_HOME, name='Bamboo Agent', env_cleanup=True)
