import docker

def check_existing(user):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    if client.containers.list(filters={'status': 'running', 'label': "sheru.id="+str(user.pk)}):
        return True
    return False


def create_container(user, template=None):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    if template:
        client.containers.run(
            template.image,
            template.shell,
            stdin_open = True,
            tty = True,
            detach = True,
            remove = True,
            labels = {"sheru.id": str(user.pk)}
        )
        return True
    else:
        client.containers.run(
            user.default_template.template.image,
            user.default_template.template.shell,
            stdin_open = True,
            tty = True,
            detach = True,
            remove = True,
            labels = {"sheru.id": str(user.pk)}
        )
        return True
    return False

def remove_all_existing_container(user):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    try:
        containers = client.containers.list(filters={'status': 'running', 'label': "sheru.id="+str(user.pk)})
        for c in containers:
            c.kill()
        return True
    except:
        return False