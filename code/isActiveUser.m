function ok =isActiveUser(conn, userName)
%This function validate the user and password and gives the options that the user can access 

ok=1 ; 
sql = sprintf( "SELECT id FROM tuser WHERE status=1 and code = '%s' ;", userName );
T = select(conn, sql) ; 
if isempty(T)
   ok = 0 ; 
   return ; 
end

end