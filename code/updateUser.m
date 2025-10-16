function [id, msgerror]  = updateUser(conn, udata, adata) 
msgerror = {} ;  
if udata.id == 0 
   sql = "INSERT INTO tuser(code, name, status, isadmin) " + ...
       " VALUES ('%s', '%s', %s,  %s) ; " ; 
   
   values = [ udata.code(1), udata.name(1), udata.status(1), udata.isadmin(1) ] ; 
   sql = sprintf(sql, values ) ; 
  execute(conn, sql); 
  T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
  id = T.x(1) ; 
else
 if udata.resetpassword(1)
   sql = "UPDATE tuser SET code='%s', name='%s', status=%s, isadmin=%s,  hashcode=null WHERE id=%s" ; 
 else 
   sql = "UPDATE tuser SET code='%s', name='%s', status=%s, isadmin=%s  WHERE id=%s" ; 
 end 
 values = [udata.code(1), udata.name(1), udata.status(1), udata.isadmin(1), udata.id(1)  ]; 
 sql = sprintf( sql, values ) ;  
 execute(conn, sql); 
 
 id = udata.id(1) ; 
end
saveSignature(conn, udata.signatureData, id) ; 
msgerror = updateUserAccess(conn, udata.id(1), adata ) ; 
commit(conn) ; 

end