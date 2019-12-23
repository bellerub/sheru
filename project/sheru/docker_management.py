import docker

def create_container(client, user, uid, template=None):

    if template:
        return client.containers.run(
            template.image,
            template.shell,
            stdin_open = True,
            tty = True,
            detach = True,
            remove = True,
            labels = {"sheru.id": str(uid), "sheru.user": str(user.pk)}
        )

    return client.containers.run(
        user.default_template.template.image,
        user.default_template.template.shell,
        stdin_open = True,
        tty = True,
        detach = True,
        remove = True,
        labels = {"sheru.id": str(uid), "sheru.user": str(user.pk)}
    )



def remove_all_existing_container(user):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    try:
        containers = client.containers.list(filters={'status': 'running', 'label': "sheru.id="+str(user.pk)})
        for c in containers:
            c.kill()
        return True
    except:
        return False