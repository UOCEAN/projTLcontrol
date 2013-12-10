from twisted.internet import reactor, protocol, task
import sys
import OpenOPC


IconicsSim = 'ICONICS.Simulator'
IconicsDbMining = 'ICONICS.DatabaseOPCServer'

tagset = ('SimulatePLC.BOOL.In1', 'SimulatePLC.BOOL.In2')

def checkICONICS_Simulator():
    opc = OpenOPC.client()
    opc.connect(IconicsSim)

    j=0
    for i in tagset:
        print i, ": ", opc[i]
        j = j+1

    opc.close()

class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clientConnectionMade(self)
        print "clients are ", self.factory.clients
    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)
    def dataReceived(self, data):
        data = data.strip()
        print "data is ", data
        if data == "stop":
            print "Program quit!!"
            reactor.stop()
            
    def message(self, message):
        self.transport.write(message + '\n')


class MyFactory(protocol.Factory):
    protocol = MyProtocol
    
    def __init__(self):
        self.clients = []
        self.lc = task.LoopingCall(self.announce)
        self.lc.start(3)

    def announce(self):
        #3 sec task
        checkICONICS_Simulator()
        print "3s delay"
        
    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

try:
    myfactory = MyFactory()
    reactor.listenTCP(5000, myfactory)
    reactor.run()
    quit()

except:
    print('Exceptional, program end')
    quit()


