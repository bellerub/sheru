from channels.generic.websocket import WebsocketConsumer
import docker
import threading
import logging

logger = logging.getLogger('django')

class CommandConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['cid']
        self.term_height = self.scope['url_route']['kwargs']['th']
        self.term_width = self.scope['url_route']['kwargs']['tw']
        self.accept()

        # Connect to Docker API, get container ID
        self.client=docker.APIClient(base_url='unix://var/run/docker.sock')
        self.container_id = self.client.containers(quiet=1, filters={'status': 'running', 'label': "sheru.id="+self.user_id})[0]['Id']

        # Push logs
        self.send(text_data=self.client.logs(self.container_id,stdout=True, stderr=True).decode('utf-8'))

        # Create & Connect to Exec
        logger.info('Exec\'ing into '+self.container_id)
        self.ex = self.client.exec_create(self.container_id, 'sh', tty=True, stdin=True)
        x = self.client.exec_start(self.ex, tty=True, stream=True, demux=True, socket=True, double_return=True)
        self.client.exec_resize(self.ex, height=self.term_height, width=self.term_width)
        self.socket = x['socket']
        self.stream = x['stream']

        # Start thread acquisition stdoutï¼Œstdinï¼Œlogs data stream
        logger.info('Start the thread')
        self.stop_thread=False
        self.t = threading.Thread(target=self.send_stream_log)
        self.t.start()

    def disconnect(self, close_code):
        # Close Thread & shutdwon socket
        logger.info('Stopping the thread and closing the socket')
        self.stop_thread=True
        self.socket._sock.send('exit\r\n'.encode('utf-8'))
        self.socket.close()

        # Close & delete container
        logger.info('Stopping and removing ' + self.container_id)
        self.client.stop(self.container_id)
        self.client.wait(self.container_id)
        self.client.remove_container(self.container_id)

        #client closed
        self.client.close()

    def receive(self, text_data):
        self.socket._sock.send(text_data.encode('utf-8'))
        logger.debug('CommandConsumer:receive')

    def send_stream_log(self):
        for b in self.stream:
            logger.debug(b)
            if self.stop_thread:
                break
            if b[0]:
                self.send(text_data=b[0].decode('utf-8'))
            if b[1]:
                self.send(text_data=b[1].decode('utf-8'))
        logger.info('Exit the thread')