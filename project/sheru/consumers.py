from .docker_management import create_container
from channels.generic.websocket import WebsocketConsumer
from .models import ContainerTemplate
import docker, sys, threading, logging

logger = logging.getLogger('django')

class CommandConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['uid']
        self.templ_id = self.scope['url_route']['kwargs']['ctid']
        self.term_height = self.scope['url_route']['kwargs']['th']
        self.term_width = self.scope['url_route']['kwargs']['tw']
        self.accept()

        user = self.scope['user']

        # Connect to Docker API
        self.client=docker.DockerClient(base_url='unix://var/run/docker.sock')
        
        # Get the Template
        try:
            templ = user.container_templates.get(pk=self.templ_id)
        except ContainerTemplate.DoesNotExist:
            # should't ever get here but just in case ...
            self.send(text_data="\u001b[33mCouldn't find template \u001b[36m" + str(self.templ_id) + "\u001b[33m, using default instead.\u001b[0m\r\n")    
            templ = user.default_template.template

        # Check for the image, pull if not found
        try:
            self.client.images.get(templ.image)
        except docker.errors.ImageNotFound:
            self.send(text_data="Image \"\u001b[36m" + templ.image + "\u001b[0m\" not found locally. Pulling image...")
            try: 
                self.client.images.pull(templ.image)
                self.send(text_data="\u001b[32m Done!\u001b[0m\r\n\r\n")
            except:
                self.send(text_data="\u001b[31m Failed!\r\n\r\nError: " + str(sys.exc_info()[1]) + "\u001b[0m\r\n")
                # 4004: Image not found ;)
                self.close(code=4004)
                return None

        # Check for new version of image
        try:
            if self.client.images.get(templ.image).attrs['RepoDigests'][0].split('@')[1] != self.client.images.get_registry_data(templ.image).id:
                self.send(text_data="\u001b[33mA new version of \u001b[36m" + templ.image + " \u001b[33mis available to be pulled down.\u001b[0m\r\n\r\n")
        except:
            logger.info("Unable to compare local image " + templ.image + " to remote repository.")

        # Create Container
        self.container = create_container(self.client, user, self.user_id, templ)
        self.container_id = self.container.id

        # Push logs
        self.send(text_data=self.client.api.logs(self.container_id,stdout=True, stderr=True).decode('utf-8'))

        # Resize TTY and attach socket
        self.container.resize(height=self.term_height, width=self.term_width)
        self.socket=self.client.api.attach_socket(self.container_id, params={'stdin': 1, 'stream': 1})

        # Start thread acquisition stdout & stdin logs data stream
        logger.info('Start the thread')
        self.stop_thread=False
        self.t = threading.Thread(target=self.send_stream_log)
        self.t.start()

    def disconnect(self, close_code):
        # if not closing because I gave error code
        if close_code < 4000:
            # Close Thread & shutdwon socket
            logger.info('Stopping the thread and closing the socket')
            self.stop_thread=True
            self.socket.close()

            logger.info('Stopping and removing ' + self.container_id)
            #self.client.api.stop(self.container_id)
            #self.client.api.wait(self.container_id)
            self.client.api.remove_container(self.container_id, force=True)

        #client closed
        self.client.close()

    def receive(self, text_data):
        self.socket._sock.send(text_data.encode('utf-8'))
        logger.debug('CommandConsumer:receive')

    def send_stream_log(self):
        for b in self.client.api.attach(self.container_id,stderr=True,stdout=True,stream=True,demux=True):
            logger.debug(b)
            if self.stop_thread:
                break
            if b[0]:
                self.send(text_data=b[0].decode('utf-8', 'ignore'))
            if b[1]:
                self.send(text_data=b[1].decode('utf-8', 'ignore'))
        logger.info('Exit the thread')