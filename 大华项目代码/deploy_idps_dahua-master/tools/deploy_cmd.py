import re
import subprocess
import time
import yaml
import sys

ENABLE_REVERT = False
CHECK_ZERO_REPLICA_TIMES = 20

COMPOSE_FILES = ['docker-compose.yml', 'evaluate-extract-compose.yml', 'extract-compose.yml']


def _get_cmd_return_code(cmd):
    sys.stdout.flush()
    sys.stderr.flush()
    return_code = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True).wait()
    return return_code


def _get_cmd_output(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output_lines = []
    while process.poll() is None:
        line = process.stdout.readline()
        line = line.strip()
        if line:
            output_lines.append(line)
    return_code = process.returncode
    return output_lines, return_code


def _print_green(content):
    print('\033[1;32m{}\033[0m'.format(content))


def _print_red(content):
    print('\033[1;31m{}\033[0m'.format(content))


def _is_docker_compose_up_required(msg):
    return 'compose' in msg


def _get_restart_required_modules(msg):
    services_modified = _get_conf_changed_module(msg)
    if services_modified:
        _print_green('The following modules have updated the configuration:')
        _print_green('\n'.join(services_modified))
    return services_modified


def _get_conf_changed_module(msg):
    module_dirs = []
    for line in msg.split('\n'):
        if re.match('^data/.*?/conf/', line.strip()) or re.match('^data/.*?/scripts/', line.strip()):
            module_dirs.append(line.split('/')[1])
    module_dirs = list(set(module_dirs))
    services_all = []
    for compose_file in COMPOSE_FILES:
        services_all.extend(yaml.load(open(compose_file))['services'])
    services_candidate = [
        s for m in module_dirs
        for s in [m, m + '_online', m + '_offline', 'evaluate_' + m, 'evaluate_' + m + '_online']
    ]
    if 'diff' in services_candidate:
        services_candidate.append('contract_diff')
        services_candidate.remove('diff')
    if 'check' in services_candidate:
        services_candidate.append('contract_check')
        services_candidate.remove('check')
    services_modified = set(services_all) & set(services_candidate)
    return services_modified


def _restart_module(module, stack_name):
    cmd = 'docker service update --force {}_{}'.format(stack_name, module)
    _print_green(cmd)
    return _get_cmd_return_code(cmd)


def _get_zero_replica_images(stack_name):
    cmd = "docker stack services %s | grep '0/[0-9]' | awk '{print $2}'" % stack_name
    output_lines, _ = _get_cmd_output(cmd)
    if output_lines:
        return output_lines


def _update_images(stack_name):
    deploy_cmd = 'docker stack deploy --with-registry-auth --prune -c docker-compose.yml -c evaluate-extract-compose.yml -c extract-compose.yml -c docker-compose.override.yml {}'.format(
        stack_name)
    _print_green(deploy_cmd)
    stack_deploy_failed = _get_cmd_return_code(deploy_cmd)

    zero_replica_images = _get_zero_replica_images(stack_name)
    recheck_time = CHECK_ZERO_REPLICA_TIMES
    while recheck_time and zero_replica_images:
        time.sleep(3)
        zero_replica_images = _get_zero_replica_images(stack_name)
        recheck_time -= 1
    is_failed = stack_deploy_failed or zero_replica_images
    if is_failed:
        _print_red('********************update image failed!********************')
        if stack_deploy_failed:
            _print_red('stack_deploy_failed')
        if zero_replica_images:
            _print_red('the following images has 0 replicas:')
            for image in zero_replica_images:
                if '_' in image:
                    image_name = image.split('_', 1)[1]
                    _print_red(image_name)
                else:
                    _print_red(image)
                log_cmd = 'docker service logs {}'.format(image)
                log, _ = _get_cmd_output(log_cmd)
                _print_green(log_cmd)
                _print_red('\n'.join(log))
        if ENABLE_REVERT:
            _print_green('failure revert is enabled, start revert...')
            _get_cmd_return_code('git revert HEAD && git push && {}'.format(deploy_cmd))
        else:
            _print_green('failure revert is disabled')
        return 1
    return 0


def deploy(_branch_name, _always_restart=False):
    stack_name = 'deploy' + _branch_name.replace('.', '').replace('_', '')
    msg = open('pull_msg.txt').read()
    _get_cmd_return_code('rm pull_msg.txt')

    _print_green('********************start to update********************')
    if _is_docker_compose_up_required(msg) or _always_restart:
        return_code = _update_images(stack_name)
        if return_code:
            exit(return_code)
    _print_green('********************start to restart********************')
    module_modified = _get_restart_required_modules(msg)
    if module_modified:
        for service in module_modified:
            return_code = _restart_module(service, stack_name)
            if return_code:
                exit(return_code)
    else:
        _print_green('no module need to restart')


if __name__ == '__main__':
    branch_name = sys.argv[1]
    always_restart = False
    if len(sys.argv) >= 3:
        always_restart = sys.argv[2] == 'true'
    deploy(branch_name, always_restart)
