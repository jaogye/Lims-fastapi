function id = checkFK( conn, sql, values )
id = 0 ; 
sql = sprintf( sql , values) ; 
T = select(conn,sql) ; 
if height(T) == 0 
  else
   id = T.id(1) ; 
end

end % checkFK

