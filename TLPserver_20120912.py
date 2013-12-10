#Traffic Light Control Proxy Server
#
# twisted.internet.protocol.Protocol
# twisted.internet.protocol.Factory
# twisted.internet.protocol.ClientFactory
#
from twisted.internet import reactor, protocol, task
import unicodedata

#database define
import pyodbc
DBfile = 'C:\projTLcontrol\DB_TLcontrol.mdb'
conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+DBfile)
cursor = conn.cursor()

#Global variable
siteNameSet = ("TLA", "TLB", "TLC", "TLD", "TLE", "TLF", "FH1", "FH2")
pollDbTime = 5 #polling database timer
oldTLAStatus = "0"
#oldTLA_HMICMD = "0"
oldTLX_HMICMD = ["0","0","0","0","0","0","0","0"]
oldTLX_Status = ("0","0","0","0","0","0","0","0")
svrListenPort = 5000

#init database while startup
def initDatabase():
    for initSite in siteNameSet:
        print 'Initiate TL_TABLE of site: ' + initSite
        SQL = "UPDATE TL_TABLE SET TLX_HMICMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMD=" + "'" + "0" + "'" + \
        ", TLX_LASTCMDBY=" + "'" + "NIL" + "'" + \
        " WHERE TLX=" + "'" + initSite + "'"
        cursor.execute(SQL)
        cursor.commit()

#check Databse HMI tags change or not
def checkDatabase():
    global oldTLA_HMICMD
    msgReturn = ""
    TLA_lastSentBy = ""
    
    SQL = 'SELECT TLX, TLX_HMICMD FROM TL_TABLE;'
    for row in cursor.execute(SQL): # cursors are iterable
        if row.TLX == "TLA":
            if (row.TLX_HMICMD != oldTLX_HMICMD[0]):
            # value changed
                oldTLX_HMICMD[0] = row.TLX_HMICMD
                if (oldTLX_HMICMD[0] == "0"):
                    msgReturn = "TLA@" + "OFF"
                else:
                    msgReturn = "TLA@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLA" + "'"
                cursor.execute(SQL1 + SQL2)
                cursor.commit()
                return msgReturn
            else:
                msgReturn = "NIL"
        elif row.TLX == "TLB":
            if (row.TLX_HMICMD != oldTLX_HMICMD[1]):
            # value changed
                oldTLX_HMICMD[1] = row.TLX_HMICMD
                if (oldTLX_HMICMD[1] == "0"):
                    msgReturn = "TLB@" + "OFF"
                else:
                    msgReturn = "TLB@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLB" + "'"
                cursor.execute(SQL1 + SQL2)
                cursor.commit()
                return msgReturn
            else:
                msgReturn = "NIL"
        elif row.TLX == "TLC":
            if (row.TLX_HMICMD != oldTLX_HMICMD[2]):
            # value changed
                oldTLX_HMICMD[2] = row.TLX_HMICMD
                if (oldTLX_HMICMD[2] == "0"):
                    msgReturn = "TLC@" + "OFF"
                else:
                    msgReturn = "TLC@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLC" + "'"
                cursor.execute(SQL1 + SQL2)
                cursor.commit()
                return msgReturn
            else:
                msgReturn = "NIL"
        elif row.TLX == "TLD":
            if (row.TLX_HMICMD != oldTLX_HMICMD[3]):
            # value changed
                oldTLX_HMICMD[3] = row.TLX_HMICMD
                if (oldTLX_HMICMD[3] == "0"):
                    msgReturn = "TLD@" + "OFF"
                else:
                    msgReturn = "TLD@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLD" + "'"
                cursor.execute(SQL1 + SQL2)
                cursor.commit()
                return msgReturn
            else:
                msgReturn = "NIL"
        elif row.TLX == "TLE":
            if (row.TLX_HMICMD != oldTLX_HMICMD[4]):
            # value changed
                oldTLX_HMICMD[4] = row.TLX_HMICMD
                if (oldTLX_HMICMD[4] == "0"):
                    msgReturn = "TLE@" + "OFF"
                else:
                    msgReturn = "TLE@" + "ON"
                TLA_lastSentBy = "HMI"
                SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMDBY="
                SQL2 = "'" + "HMI" + "'"+ " WHERE TLX=" + "'" + "TLE" + "'"
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
        print "clients connection made: ", self.factory.clients
        print "no of clients connected: ", self.factory.numClients
        
    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

    #data received from client    
    def dataReceived(self, data):
        #print "raw data rx:", data
        data = data.replace('\r\n','')
        print 'raw data:', data
        
        a = data.split(':')
        if len(a) > 1:
            command = a[0]
            content = a[1]

            msg = ""
            if command == "iam":
                self.name = content.replace('\r\n','') #remove crlf
                print 'client: ' + self.name + ' added.'
                msg = "svr:" + self.name + "@add"
                for c in self.factory.clients:
                    c.message(msg)
            elif command == "msg":
                print "message received from " + self.name + " said:" + content
                msg = self.name + ":" + content #msg will be broadcast

                # decode cmd
                b = content.split('@')
                if (len(b) > 1):
                    if (b[0] in siteNameSet):
                        sitename = b[0]
                        cmd = b[1]
                        cmd = cmd.replace('\r\n','')  #remove CR LF at the end
                        if cmd == "ON":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMD="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'1'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "OFF":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMD="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'0'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "ACNG":
                            SQL1 = "UPDATE TL_TABLE SET TLX_AC="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'1'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "ACOK":
                            SQL1 = "UPDATE TL_TABLE SET TLX_AC="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'0'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "LANON":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LANTERN="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'1'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "LANOFF":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LANTERN="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'0'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "LAMPNG":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LAMP="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'1'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        elif cmd == "LAMPOK":
                            SQL1 = "UPDATE TL_TABLE SET TLX_LAMP="
                            SQL2 = ", TLX_LASTCMDBY=" + "'"
                            SQL3 = "'" + " WHERE TLX="
                            SQL = ""
                            cmd1 = "'0'"
                            cmd2 = self.name
                            cmd3 = "'" + sitename + "'"
                            SQL = SQL1 +cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                            print SQL
                            cursor.execute(SQL)
                            cursor.commit()
                        else:
                            print "**Command unknown!! ", cmd

                        #SQL1 = "UPDATE TL_TABLE SET TLX_LASTCMD="
                        #SQL2 = ", TLX_LASTCMDBY=" + "'"
                        #SQL3 = "'" + " WHERE TLX="
                        #SQL=""
                        #cmd1=""
                        #cmd2=""
                        #cmd3=""
                        #cmd2 = self.name
                        #cmd3 = "'" + sitename + "'"
                        #if cmd == "ON":
                        #    cmd1 = "'1'"
                        #elif cmd == "OFF":
                        #    cmd1 = "'0'"
                        #else:
                        #    cmd1 =""
                        #    cmd2 =""
                        #    print "Command unknown!!", cmd
                            
                        #if len(cmd1) != 0:
                        #    SQL = SQL1 + cmd1 + SQL2 + cmd2 + SQL3 + cmd3
                        #    # print SQL
                        #    cursor.execute(SQL)
                        #    cursor.commit()

                        # broadcast message to other clients
                        print 'message broadcast: ', msg
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
        self.numClients = 0 
        self.clients = []
        self.lc = task.LoopingCall(self.announce)
        self.lc.start(3)

    def announce(self):
        # 3 sec task to check HMI action
        state = ""
        state = checkDatabase()  #return action of HMI, TLA@ON...
        if len(state) > 0:
            if state != "NIL":
                # broadcast HMI cmd
                msg = "svr:" + state + "\n"
                print 'message broadcast: ', msg
                type(msg)
                for client in self.clients:
                    client.transport.write(msg.encode('ascii','ignore'))
            
    def clientConnectionMade(self, client):
        self.clients.append(client)
        self.numClients = self.numClients+1
        
    def clientConnectionLost(self, client):
        print 'client disconnect'
        self.clients.remove(client)
        self.numClients = self.numClients-1

#main program 
print "Mawan Traffic Proxy Server started"
initDatabase()
myfactory = MyFactory()
reactor.listenTCP(svrListenPort, myfactory)
reactor.run()
