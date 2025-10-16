% This function checks if a table.column exists in the database 
function ok = existsColumn(conn, table, column)
ok = 0 ; 
sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS " + ...
    "WHERE TABLE_NAME = '%s' AND COLUMN_NAME='%s'" ;
sql = sprintf(sql, [table, column]) ; 
T = select(conn, sql) ; 
if height(T) > 0
   ok = 1 ; 
end

end