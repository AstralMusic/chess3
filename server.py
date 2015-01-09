# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"

# __name__ = '__main__'

import socket, sys, time, random, logging

logging.basicConfig(
   level=logging.DEBUG,
   #format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
   format='%(asctime)s:%(levelname)s:%(message)s ',
   datefmt="%Y-%m-%d %H:%M:%S",
   filename="../out.log",
   filemode='a'
)

class Client:
    def __init__(self, sock, addr):
        self.socket = sock
        self.address = addr

    def setId(self, Id):
        self.id = Id

    def setName(self, name):
        self.name = name

    def inform(self, msg):
        self.socket.send(msg)

    def __call__(self, *args, **kwargs):
        return self.socket


class Server:
    default_server_address = "92.113.247.161"
    default_server_port = 12345
    def __init__(self):
        self.address = "127.0.0.1"
        self.port = self.default_server_port

    def waitingClients(self):
        listener = socket.socket()
        self.clients = []
        #for tests assume as localhost
        listener.bind(('',self.port))
        #start listening
        listener.listen(3)
        for i in xrange(3):
            sock, addr = listener.accept()

            newClient = Client(sock,addr)
            name = newClient.socket.recv(32)
            #recieved text is wierd, so we need to
            name = name[::2]
            newClient.setName(name)

            newClient.setId(i)
            newClient.inform(str(i))

            self.clients.append(newClient)

            logging.info( "Connected new client: %s" % name )
            logging.info( "Client id = %d" % i )
            logging.info( " address: %s" % addr[0] )
            logging.info( " port: %d \n" % addr[1] )

        listener.close()

    def shoutStart(self):
        #tell every client info about other clients
        self.activePlayerId = random.randint(0,2)
        for each in self.clients:
            for client in self.clients:
                if not each == client:
                    msg = str(client.id) + client.name
                    each.inform(msg)
                    logging.info( "'%s' sended to %d" % (msg, each.id) )
                    time.sleep(.025)
            each.inform(str(self.activePlayerId))
            logging.info( "Active player Id  = '%d' sended to %d \n" % (self.activePlayerId, each.id) )

    def informClients(self):
        pass

    def turnPass(self):
        self.activePlayerId = (self.activePlayerId + 1) % 3
        logging.info( "Turn passed\n" )

    def play(self):
        #while not the only king alive
        end_of_the_game = False
        while not end_of_the_game:
            incomingMessage = self.clients[self.activePlayerId].socket.recv(10)
            logging.info( "'%s' - recived from %s (%d)" % (incomingMessage, self.clients[self.activePlayerId].name , self.activePlayerId) )
            if "turn_ended" in incomingMessage:
                time.sleep(0.025)
                for client in self.clients:
                    if client != self.clients[self.activePlayerId]:
                        client.inform("turn_ended")
                        logging.info( "'turn_ended' was sent to %s (%d)" % (client.name , client.id) )

            newCoords = list()
            for i in xrange(6):
                newCoord = int(self.clients[self.activePlayerId].socket.recv(1))
                if i == 0 or i == 3:
                    newCoord = (newCoord + self.clients[self.activePlayerId].id) % 3
                newCoords.append(int(newCoord))
            logging.info(  "Recieved sequence: %d %d %d %d %d %d " % tuple(newCoords) )


            time.sleep(.025)
            for client in self.clients:
                logging.info( "movement info: ", newCoords, " for player %s (%d)" % (client.name, client.id) )
                if client != self.clients[self.activePlayerId]:
                    for i in xrange(len(newCoords)):
                        if i == 0 or i == 3:
                            newCoords[i] = (newCoords[i] - client.id + 3) % 3
                        client.inform(str(newCoords[i]))
                        logging.info(  "Sended that coord to: %s ( %d ) and message is: %d" % (client.name, client.id, newCoords[i]) )

            self.turnPass()


    def main(self):
        try:
            self.waitingClients()
        except:
            logging.info( "Connecting with clients failed" )
        try:
            self.shoutStart()
        except:
            logging.info( "Bad connection" )
        #self.play()
        try:
            self.play()
        except:
            logging.info( "server.play() crushed" )

if __name__ == '__main__':
    program = Server()
    program.main()