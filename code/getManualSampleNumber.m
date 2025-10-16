function newSampleNumber = getManualSampleNumber(conn, sdate)

sql = "SELECT count(*) cnt FROM Sample WHERE typesample='MAN' AND loadingdate='%s'; " ; 
sql = sprintf(sql, sdate) ; 
T = select(conn, sql ) ; 
x = T.cnt(1) + 1 ; 
newSampleNumber = "M_" + datestr(now,'ddmmyyyy') + "_" + sprintf('%03d',x) ;

end 