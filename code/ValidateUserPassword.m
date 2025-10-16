function [ok, iduser, useroptions]  =ValidateUserPassword(conn, userName,password)
 
%This function validate the user and password and gives the options that the user can access 

ok=1 ; 
iduser=0; 
useroptions = {}  ; 
userName = strtrim(userName) ; 
sql = sprintf( "SELECT id, hashcode FROM tuser WHERE code = '%s' ;", userName );
T = select(conn, sql) ; 
if isempty(T)
   ok = 0 ; 
   return ; 
end

hh = getHashCode(string(userName) + string(password) ,password) ; 
iduser = T.id(1) ; hashcode = T.hashcode(1); 
if not( strcmp(hashcode, hh) )
   ok = 0 ; 
   return ;    
end

sql = sprintf( "SELECT om.name opt FROM optionUser ou, optionMenu om " + ...
    "WHERE om.id=ou.option_id and user_id = %d ;", iduser );
O = select(conn, sql) ; 

if height(O) == 0
   useroptions = {} ; 
else 
   useroptions = strtrim(O.opt) ; 
end 

end


