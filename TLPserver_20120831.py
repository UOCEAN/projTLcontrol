from twisted.internet import reactor, protocol, task
import unicodedata


#database define
import pyodbc
DBfile = 'C:\projTLcontrol\DB_TLcontrol.mdb'
conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+DBfile)
cursor = conn.cursor()
siteNameSet = ("TLA", "TLB", "TLC", "TLD", "TLE", "TLF", "FH1", "FH2")
pollDbTime = 5 #polling database timer
oldTLAStatus = "0"
oldTLA_HMICMD = "0"
svrListenPort = 5000

def initDatabase():
    # init database while startup
    SQL = "UPDATE TL_TABLE SET TLX_HMICMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMDBY=" + "'" + "NIL" + "'" + \
        " WHERE TLX=" + "'" + "TLA" + "'" 
    print SQL
    cursor.execute(SQL)
    cursor.commit()

    SQL = "UPDATE TL_TABLE SET TLX_HMICMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMDBY=" + "'" + "NIL" + "'" + \
        " WHERE TLX=" + "'" + "TLB" + "'" 
    print SQL
    cursor.execute(SQL)
    cursor.commit()


def checkDatabase():
    # check Database HMI change the value or not
    global oldTLA_HMICMD
    msgReturn = ""
    TLA_lastSentBy = ""
    
    SQL = 'SELECT TLX, TLX_HMICMD FROM TL_TABLE;'
    for row in cursor.execute(SQL): # cursors are iterable
        if row.TLX == "TLA":
            if (row.TLX_HMICMD != oldTLA_HMICMD):
            # value changed
                print "value changed"
                oldTLA_HMICMD = row.TLX_HMICMD
                if (oldTLA_HMICMD == "0"):
                    msgReturn = "TLA@" + "OFF"
                else:
                    msgReturn = "TLA@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLA" + "'"
                print SQL1 + SQL2
                cursor.execute(SQL1 + SQL2)
                cursor.commit()
                return msgReturn
            else:
                msgReturn = "NIL"
        else:
            msgReturn = "NIL"

    return msgReturn

class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clientConnectionMade(self)
        print "clients are ", self.factory.clients
    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)
    def dataReceived(self, data):
        #print "data is ", data
        a = data.split(':')
        if len(a) > 1:
            command = a[0]
            content = a[1]

            msg = ""
            if command == "iam":
                self.name = content
                msg = self.name + " has joined"
                print msg
                for c in self.factory.clients:
                    c.message(msg)
            elif command == "msg":
                print "message received: " + msg
                msg = self.name + ": " + content
                b = content.split('@')
                if (len(b) > 1):
                    if (b[0] in siteNameSet):
                        sitename = b[0]
                        cmd = b[1]
                        print self.name + " command rx " + sitename + " " + cmd
                        cmd = cmd.replace('\r\n','')  #remove CR LF at the end
                        SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMD="
                        SQL2 = ", TLX_LASTCMDBY=" + "'"
                        SQL3 = "'" + " WHERE TLX="
                        SQL=""
                        cmd1=""
                        cmd2=""
                        cmd3=""
                        cmd2 = self.name
                        cmd3 = "'" + sitename + "'"
                        if cmd == "ON":
                            cmd1 = "'1'"
                        elif cmd == "OFF":
                            cmd1 = "'0'"
                        else:
                            cmd1 =""
                            cmd2 =""
                            print "Command unknown!!"
                            
                        if len(cmd1) != 0:
                            SQL = SQL1 + cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            # print SQL
                            cursor.execute(SQL)
                            cursor.commit()

                        # broadcast message to other clients
                        for c in self.factory.clients:
                            c.message(msg)
                    else:
                        print "Site name unknown!!!"
                        
    def message(self, message):
        self.transport.write(message + '\n')
        
class MyFactory(protocol.Factory):
    oldTLAStatus = ""
    protocol = MyProtocol
    
    def __init__(self):
        self.clients = []
        self.lc = task.LoopingCall(self.announce)
        self.lc.start(3)

    def announce(self):
        #for testing 
        #for client in self.clients:
        #    client.transport.write("svr:3s Pulse\n")
        state = ""
        state = checkDatabase()
        if len(state) > 0:
            if state != "NIL":
                # encode to ASCII
                msg = "svr: " + state + "\n"
                type(msg)
                # unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore')
                # print msg.encode('ascii','ignore')
                for client in self.clients:
                    client.transport.write(msg.encode('ascii','ignore'))
            
    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

print "Mawan Traffic Proxy Server started"
initDatabase()
myfactory = MyFactory()
reactor.listenTCP(svrListenPort, myfactory)
reactor.run()
