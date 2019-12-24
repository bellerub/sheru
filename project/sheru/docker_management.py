import docker
from .models import User

class ContainerPermissionDenied(Exception):
    pass

def create_container(client, user, uid, template=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    if template == None:
        template = user.default_template.template

    # Build ParameterSet
    kwargs = {
        'stdin_open': True,
        'tty': True,
        'detach': True,
        'remove': True,
        'labels': {"sheru.id": str(uid), "sheru.user": str(user.pk)},
        'working_dir': template.working_dir
    }

    if template.network_disable:
        kwargs['network_disabled'] = True
    elif template.dns_server_1:
        if template.dns_server_2:
            kwargs['dns'] = [template.dns_server_1, template.dns_server_2]
        else:
            kwargs['dns'] = [template.dns_server_1]
    if template.dns_search_domain: kwargs['dns_search'] = [template.dns_search_domain]
    if template.user_id: kwargs['user'] = template.user_id

    # TODO logic for volumes   

    return client.containers.run(template.image, template.shell, **kwargs)

def get_running_containers(user_pk=None, client=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    # Get containers
    if user_pk == None:
        containers = client.containers.list(filters={'status': 'running', 'label': "sheru.user"})
    else:
        containers = client.containers.list(filters={'status': 'running', 'label': "sheru.user="+str(user_pk)})
    results = list()
    for c in containers:
        results.append(
            {
                "user": User.objects.get(pk=c.attrs['Config']['Labels']['sheru.user']),
                "session": str(c.attrs['Config']['Labels']['sheru.id']),
                "image": c.attrs['Config']['Image'],
                "id": c.id,
                "created": c.attrs['Created']
            }
        )
    return results

def kill_container(container_id, client=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # Get Container & make sure it has a session id
    container = client.containers.get(container_id)
    if 'sheru.id' in container.attrs['Config']['Labels']:
        container.remove(force=True)
    else:
        raise ContainerPermissionDenied