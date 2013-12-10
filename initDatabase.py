
def initDatabase(db):
    # init database while startup
    SQL = "UPDATE TL_TABLE SET TLX_HMICMD=" + "'" + "1" + "'" + \
        ", TLX_LASTCMD=" + "'" + "1" + "'" + \
        ", TLX_LASTCMDBY=" + "'" + "NIL" + "'" + \
        " WHERE TLX=" + "'" + "TLA" + "'" 
    print SQL
    db.execute(SQL)
    db.commit()
    

