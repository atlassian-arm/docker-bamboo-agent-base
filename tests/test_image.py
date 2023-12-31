import pytest
import time

from helpers import get_app_home, get_app_install_dir, get_bootstrap_proc, get_procs, \
    parse_properties, parse_xml, run_image, wait_for_http_response, wait_for_proc


BOOTSTRAP_PROC = 'com.atlassian.bamboo.agent.bootstrap.AgentBootstrap'

def test_wrapper_conf(docker_cli, image, run_user):
    environment = {
        'BAMBOO_SERVER': 'http://localhost',
        'WRAPPER_JAVA_INITMEMORY': '383',
        'WRAPPER_JAVA_MAXMEMORY': '576',
        'IGNORE_SERVER_CERT_NAME': 'true',
        'ALLOW_EMPTY_ARTIFACTS': 'true',
        'AGENT_EPHEMERAL_FOR_KEY': 'PROJ-PLAN-JOB1-1',
        'SECURITY_TOKEN': '123'
    }
    container = run_image(docker_cli, image, user=run_user, environment=environment)
    _jvm = wait_for_proc(container, BOOTSTRAP_PROC)

    procs_list = get_procs(container)
    jvm = [proc for proc in procs_list if BOOTSTRAP_PROC in proc][0]

    assert environment["BAMBOO_SERVER"] in jvm
    assert environment["SECURITY_TOKEN"] in jvm
    assert f'-Xms{environment["WRAPPER_JAVA_INITMEMORY"]}m' in jvm
    assert f'-Xmx{environment["WRAPPER_JAVA_MAXMEMORY"]}m' in jvm
    assert f'-Dbamboo.agent.ignoreServerCertName={environment["IGNORE_SERVER_CERT_NAME"]}' in jvm
    assert f'-Dbamboo.allow.empty.artifacts={environment["ALLOW_EMPTY_ARTIFACTS"]}' in jvm
    assert f'-Dbamboo.agent.ephemeral.for.key={environment["AGENT_EPHEMERAL_FOR_KEY"]}' in jvm

def test_wrapper_conf_with_bamboo_ephemeral_agent_data(docker_cli, image, run_user):
    bamboo_server_val = 'http://localhost/override'
    token_val = '123'
    launch_reason = 'PROJ-PLAN-JOB1-1'
    environment = {
        'WRAPPER_JAVA_INITMEMORY': '383',
        'WRAPPER_JAVA_MAXMEMORY': '576',
        'IGNORE_SERVER_CERT_NAME': 'true',
        'ALLOW_EMPTY_ARTIFACTS': 'true',
        'AGENT_EPHEMERAL_FOR_KEY': 'PROJ-PLAN-JOB1-2', # the for_key from BAMBOO_EPHEMERAL_AGENT_DATA has higher priority than the explicitly passed one
        'BAMBOO_EPHEMERAL_AGENT_DATA': f'BAMBOO_SERVER={bamboo_server_val}#SECURITY_TOKEN={token_val}#bamboo.agent.ephemeral.for.key={launch_reason}'
    }
    container = run_image(docker_cli, image, user=run_user, environment=environment)
    _jvm = wait_for_proc(container, BOOTSTRAP_PROC)

    procs_list = get_procs(container)
    jvm = [proc for proc in procs_list if BOOTSTRAP_PROC in proc][0]

    assert bamboo_server_val + '/agentServer' in jvm
    assert token_val in jvm # token
    assert f'-Xms{environment["WRAPPER_JAVA_INITMEMORY"]}m' in jvm
    assert f'-Xmx{environment["WRAPPER_JAVA_MAXMEMORY"]}m' in jvm
    assert f'-Dbamboo.agent.ignoreServerCertName={environment["IGNORE_SERVER_CERT_NAME"]}' in jvm
    assert f'-Dbamboo.allow.empty.artifacts={environment["ALLOW_EMPTY_ARTIFACTS"]}' in jvm
    assert f'-Dbamboo.agent.ephemeral.for.key={launch_reason}' in jvm

def test_startup_probe(docker_cli, image, run_user):
    environment = {
        'BAMBOO_SERVER': 'http://localhost',
        'BAMBOO_AGENT_PERMISSIVE_READINESS': 'true',
    }

    container = docker_cli.containers.run(image, detach=True, user=run_user, environment=environment)

    for i in range(10*60):
        (exit_code, _output) = container.exec_run('/probe-startup.sh')
        if exit_code == 0:
            return
        time.sleep(0.1)

    assert False

def test_readiness_probe(docker_cli, image, run_user):
    environment = {
        'BAMBOO_SERVER': 'http://localhost',
        'BAMBOO_AGENT_PERMISSIVE_READINESS': 'true',
    }

    container = docker_cli.containers.run(image, detach=True, user=run_user, environment=environment)

    for i in range(10*60):
        (exit_code, _output) = container.exec_run('/probe-readiness.sh')
        if exit_code == 0:
            return
        time.sleep(0.1)

    assert False
