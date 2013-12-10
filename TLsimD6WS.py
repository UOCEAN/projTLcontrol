#Traffic Light Control Simulate D6 WS
# to control the RF Modem and receive signal from remote site
#
#
from twisted.internet import reactor, protocol, task

#Global variable
HOST = 'localhost'
PORT = 5000
siteNameSet = ("TLA", "TLB", "TLC", "TLD", "TLE", "TLF", "FH1", "FH2")
pollDbTime = 5 #polling database timer
oldTLAStatus = "0"
oldTLA_HMICMD = "0"
svrListenPort = 5000


class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        print "server connected"
        
        
    #data received from client    
    def dataReceived(self, data):
        print "data is ", data
                        
    #def message(self, message):
    #    self.transport.write(message + '\n')
        
class MyFactory(protocol.Factory):
    protocol = MyProtocol
    
    def __init__(self):
        print 'MyFactory init'
        print 'setup 3s task'
        self.lc = task.LoopingCall(self.announce)
        self.lc.start(3)
        
    def announce(self):
        # 3 sec task to check HMI action
        print '3s task'
            
    
#main program 
print "Mawan Traffic Traffic Control Simulator Started"
factory = MyFactory()
reactor.connectTCP(HOST, PORT, factory)
reactor.run()
