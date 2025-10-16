function DeleteQualityInfo(conn, SampleNumber) 

sql = "SELECT id from sample where samplenumber='%s' " ;  
sql = sprintf( sql, SampleNumber ) ; 
T = select(conn, sql) ; 

delete = "Delete from measurement where sample_id = %d " ; 
delete = sprintf( delete, T.id ) ; 
execute(conn, delete) ; 

end