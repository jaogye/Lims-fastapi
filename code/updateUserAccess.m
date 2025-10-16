function msgerror = updateUserAccess(conn, iduser, data ) 
msgerror = {} ; 

sql = "DELETE FROM optionuser  WHERE user_id=%d ; " ;          
sql = sprintf(sql, iduser) ; 
execute(conn, sql ) ;        

for i=1:height(data)
    option_id = data.option_id(i);
    if data.Flag(i) 
        sql = "INSERT INTO optionuser(user_id, option_id) VALUES(%d,%d)" ;
       values = [iduser, option_id ] ; 
       sql = sprintf(sql, values) ; 
       execute(conn, sql ) ;        
    end 
end
commit(conn) ; 
end