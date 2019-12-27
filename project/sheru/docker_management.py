import docker
from .models import User

class ContainerPermissionDenied(Exception):
    pass

class DefaultUserVolumeExists(Exception):
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
        'labels': {"xyz.sheru.id": str(uid), "xyz.sheru.user": str(user.pk)},
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

    if template.mount_volume:
        # get default volume
        vol = get_volumes(user.pk, True, client)
        if not vol:
            vol = create_volume(user.pk, client)
        kwargs['volumes'] = {vol[0]['name']: {
            'bind': template.mount_location,
            'mode': 'rw'
        }}
    return client.containers.run(template.image, template.shell, **kwargs)

def get_running_containers(user_pk=None, client=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    # Get containers
    if user_pk == None:
        containers = client.containers.list(filters={'status': 'running', 'label': "xyz.sheru.user"})
    else:
        containers = client.containers.list(filters={'status': 'running', 'label': "xyz.sheru.user="+str(user_pk)})
    results = list()
    for c in containers:
        results.append(
            {
                "user": User.objects.get(pk=c.attrs['Config']['Labels']['xyz.sheru.user']),
                "session": str(c.attrs['Config']['Labels']['xyz.sheru.id']),
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
    if 'xyz.sheru.id' in container.attrs['Config']['Labels']:
        container.remove(force=True)
    else:
        raise ContainerPermissionDenied

#   get_volumes
#       
#   Returns list of sheru volumes - either by user or all users
#   If default == True, should return list of default volumes
#   
#   There should never be more than one default vol per user,
#   otherwise will use first volume returned by docker api
#
def get_volumes(user_pk=None, default=False, client=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # Get Volumes
    if user_pk == None and default == False:
        vols = client.volumes.list(filters={'label': "xyz.sheru.user"})
    elif user_pk and default == False:
        vols = client.volumes.list(filters={'label': "xyz.sheru.user="+str(user_pk)})
    elif user_pk == None and default:
        vols = client.volumes.list(filters={'label': ["xyz.sheru.user", 'xyz.sheru.default']})
    else:
        vols = client.volumes.list(filters={'label': ["xyz.sheru.user="+str(user_pk), 'xyz.sheru.default']})
    results = list()
    for v in vols:
        is_default = True if 'xyz.sheru.default' in v.attrs['Labels'] else False
        results.append(
            {
                "user": User.objects.get(pk=v.attrs['Labels']['xyz.sheru.user']),
                "name": v.attrs['Name'],
                "created": v.attrs['CreatedAt'],
                "default": is_default
            }
        )
    return results

def create_volume(user_pk, client=None):
    if client == None:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    
    # check for existing volume
    if get_volumes(user_pk, True, client):
        raise DefaultUserVolumeExists

    client.volumes.create(labels={
        'xyz.sheru.user': str(user_pk),
        'xyz.sheru.default': 'True'
    })
    # consistent return
    return get_volumes(user_pk, True, client)
    