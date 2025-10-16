% This function insert into loglims table a text saving parameters to debug
function insertlog(conn, point, text)

sql = "INSERT INTO loglims(point, date, message) values('%s', '%s', '%s' )" ;
sql = sprintf(sql, point, datetime, text) ; 
execute( conn, sql)
commit(conn) ; 

end