function  ok = existPassword(conn, userName) 

ok=1 ;
userName = strtrim(userName) ; 
sql = "SELECT hashcode FROM tuser WHERE code ='%s'" ;
sql = sprintf(sql, userName) ; 
T = select(conn, sql) ; 
if isempty(T)
   ok=0; 
   return 
end    

if ismissing(T.hashcode(1))
   ok=0; 
end    

end