function msgerror = deleteManualSample(conn, id) 
msgerror = {} ; 
if id == 0 
   msgerror{1} = "It is not possible to delete the sample, it does not exist."  ; 
   return ;  
end    
sql = "SELECT id FROM measurement WHERE value>0 and sample_id =%d" ; 
sql = sprintf(sql, id ) ; 
T = select(conn, sql) ; 
if height(T) > 0
      msgerror{1} = "It is not possible to delete the sample, i contains tests entered."  ; 
   return ;  
end    

sql = "DELETE FROM Sample WHERE id=%d" ; 
sql = sprintf(sql, id ) ; 
execute(conn, sql ) ;
commit(conn) ; 


end