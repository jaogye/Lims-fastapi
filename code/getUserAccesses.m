function  [msgerror, data ] =  getUserAccesses(conn, iduser) 

iduser = string(iduser) ; 
msgerror={} ; 
sql = "SELECT  m.name, 1 flag, m.id option_id from optionuser u, " + ...
    "optionmenu m where u.user_id = %s  and u.option_id=m.id   " + ...
    "UNION  SELECT  m.name, 0 flag,  m.id option_id from optionmenu m where   " + ...
    " not exists( select * from optionuser u  where u.option_id=m.id and u.user_id = %s) " ; 
sql = sprintf(sql, [iduser, iduser]) ; 
data = select (conn, sql) ; 

end 