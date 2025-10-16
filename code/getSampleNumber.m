% This function computes the next sample number for any type of sample (CLI, PRO, MAN)
function newSampleNumber = getSampleNumber(conn, sdate, typesample)

%sql = "SELECT count(*) cnt FROM Sample WHERE typesample='PRO' AND substring(creationdate,1,10)='%s'; " ; 
sql = "SELECT count(*) cnt FROM Sample WHERE typesample='%s' AND substring(loadingdate,1,10)='%s'; " ; 
sql = sprintf(sql, typesample, sdate) ; 
T = select(conn, sql ) ; 
if T.cnt(1) > 0
   sql2 = "Select  max( substring( samplenumber,11,3)) lastsample FROM sample " + ...
       "WHERE typesample='%s' AND substring(loadingdate,1,10)='%s'; " ; 
   sql2 = sprintf(sql2, typesample, sdate) ; 
   T2 = select(conn, sql2 ) ; 
   x = str2double( T2.lastsample(1) ) + 1 ; 
else 
   x=1 ; 
end 
ss = string( extractBefore(typesample,2) ) ; 
newSampleNumber = ss + datestr(sdate,'ddmmyyyy') + "_" + sprintf('%03d',x) ;

end 

 