# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"

# __name__ = '__main__'

import socket, sys, time, random, logging , string
import default_settings

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
        self.isAlive = True

    def setKilled(self):
        self.isAlive = False

    def setId(self, Id):
        self.id = Id

    def setName(self, name):
        self.name = name

    def inform(self, msg):
        try:
            self.socket.send(msg)
        except BaseException,e:
            logging.error("Sending data to  %s (%d) failed, because of lost connection with client." % (self.name,self.id))

    def __call__(self, *args, **kwargs):
        return self.socket

class Server:
    def __init__(self):
        self.address = "127.0.0.1"
        self.port = default_settings.server_port

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

            log_message = "Connected new client: %s. " \
                          "Client id = %d. " \
                          " address: %s. " \
                          " port: %d."% (name,i,addr[0],addr[1])
            logging.debug(log_message)

        listener.close()

    def shoutStart(self):
        #tell every client info about other clients
        self.activePlayerId = random.randint(0,2)
        for each in self.clients:
            for client in self.clients:
                if not each == client:
                    msg = str(client.id) + client.name
                    each.inform(msg)
                    time.sleep(.025)
            each.inform(str(self.activePlayerId))
            logging.debug( "Informed %s (%d) about two other players and who's active player" % (each.name, each.id) )
        logging.info("FINISHED SETUP\n")

    def turnPass(self):
        if self.clients[(self.activePlayerId + 1) % 3].isAlive:
            self.activePlayerId = (self.activePlayerId + 1) % 3
        elif self.clients[(self.activePlayerId + 2) % 3].isAlive:
            self.activePlayerId = (self.activePlayerId + 2) % 3
        logging.info( "Turn passed\n")

    def play(self):
        def playersAlive():
            res = 0
            for x in self.clients:
                if x.isAlive: res += 1
            return  res
        winner = loser = None
        #while not the only player alive
        GAME_FINISHED = False
        while not GAME_FINISHED:
            incomingMessage = self.clients[self.activePlayerId].socket.recv(10)
            logging.info( "'%s' - recived from %s (%d)" %
                          (incomingMessage, self.clients[self.activePlayerId].name , self.activePlayerId) )
            if incomingMessage == '':
                self.clients[self.activePlayerId].socket.close()
                raise BaseException, "Client #%d got crazy, so I closed his socket and aborted session." %self.activePlayerId

            if "killed" in incomingMessage:
                loserId = int(incomingMessage[7])
                self.clients[loserId].setKilled()
                logging.warning("Player %s (%d) was killed by %s (%d)."\
                    %(self.clients[loserId].name,loserId,self.clients[self.activePlayerId].name,self.activePlayerId))
                self.clients[3 - loserId - self.activePlayerId].inform(incomingMessage)
                #info for the end of the game
                if not loser:
                    loser = loserId
                else: winner = self.activePlayerId

            if "turn_ended" in incomingMessage:
                time.sleep(0.025)
                for client in self.clients:
                    if client != self.clients[self.activePlayerId]:
                        client.inform("turn_ended")
                        logging.info( "'turn_ended' was sent to %s (%d)" % (client.name , client.id) )

                rcvdCoords = list()
                for i in xrange(6):
                    rcvdCoord = int(self.clients[self.activePlayerId].socket.recv(1))
                    if i == 0 or i == 3:
                        rcvdCoord = (rcvdCoord + self.activePlayerId) % 3
                    rcvdCoords.append(int(rcvdCoord))
                logging.info(  str("Recieved sequence: {0}".format(rcvdCoords) ))

                time.sleep(.025)
                for client in self.clients:
                    if client != self.clients[self.activePlayerId]:
                        logging.info(str( "movement info: " + string.join([str(i) for i in rcvdCoords]) + " for player %s (%d)" % (client.name, client.id) ))
                        newCoords = rcvdCoords[:]
                        for i in xrange(len(newCoords)):
                            if i == 0 or i == 3:
                                newCoords[i] = (newCoords[i] - client.id + 3) % 3
                            client.inform(str(newCoords[i]))
                        logging.info( str( "Sended that coords to %s ( %d ) : " % (client.name, client.id)+ string.join([str(i) for i in newCoords]) ))

                logging.info (" playersAlive() returned %d" % playersAlive())
                if playersAlive() < 2:
                    GAME_FINISHED = True
                    #break
                self.turnPass()
        if GAME_FINISHED:
            logging.info("Sending to the clients message about finished game 'finished_g'")
            for each in self.clients:
                each.inform("finished_g")
                each.inform(str(winner))
                each.inform(str(loser))


    def main(self):
        logging.info("NEW SESSION STARTED \n")
        try:
            self.waitingClients()
        except BaseException, e:
            logging.critical( "Connecting with clients failed. Error: %s." % str(e) )
        try:
            self.shoutStart()
        except BaseException, e:
            logging.critical( "Bad connection. Error: %s." % str(e) )
        try:
            self.play()
        except BaseException, e:
            logging.critical( "server.play() crushed. Error: %s." % str(e) )
            logging.info("Informing clients about end of the game...")
            for each in self.clients:
                each.inform("game_abort")

        logging.info("SESSION ENDED \n")

if __name__ == '__main__':
    program = Server()
    program.main()