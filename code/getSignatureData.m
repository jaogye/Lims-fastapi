function [signatureData, signatureAData, user_Name, admin_Name] = getSignatureData(conn, userName) 

sql = "SELECT signature, name from tuser where code = '%s' " ; 
sql = sprintf(sql, userName) ; 
T = select(conn, sql) ; 
signatureData = T.signature{1} ; 
user_Name =  string(strtrim(T.name) ); 
sql = "SELECT signature, name from tuser where isadmin=1" ; 
T = select(conn, sql) ; 
signatureAData = T.signature{1} ; 
admin_Name =  string(strtrim(T.name) ); 

end