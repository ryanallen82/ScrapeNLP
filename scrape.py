from yammer import YammerLoad, YammerFact


YL = YammerLoad()
client = YL.connect_yammer()
cnxn, cursor = YL.database_connect()
YL.get_yammer_data(cursor,cnxn,client)
YF = YammerFact()
cnxnf, cursorf, maxid = YF.database_connect()
YF.fact(cnxnf, cursorf, maxid)
YF.dim_msg(cnxnf, cursorf)