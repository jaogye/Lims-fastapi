function ok = existsQuery(conn, sql, values ) 
ok=0 ; 
if nargin == 3
   sql = sprintf(sql ,values) ;  
end    
T = select(conn, sql) ; 
if height(T) > 0
   ok = 1 ; 
end
end 
