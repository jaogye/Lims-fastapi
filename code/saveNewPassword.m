function saveNewPassword(conn, userName, NewPassword )  
userName = strtrim(userName) ;   
password = strtrim(NewPassword) ; 
hh = getHashCode(string(userName) + string(password) ,password) ; 
sql = "UPDATE tuser SET hashcode='%s' WHERE code='%s';" ; 
sql = sprintf(sql, [hh, string(userName)]) ;
execute(conn, sql) ; 
commit(conn  ) ; 
end