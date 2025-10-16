function  [msgerror, data ] =  getUsers(conn) 

msgerror={} ; 
sql = "SELECT id, code , name , hashcode, status,  isadmin,  signature from tuser ;" ; 
data = select (conn, sql) ; 

end 