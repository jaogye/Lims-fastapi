% This function saves the signature of a user with id into tuser table
function saveSignature(conn, signatureData, id)
% Create a temporary database table with a binary column that contains the
% signaturedata
tt = size(  signatureData ) ; 
if tt(2) == 1  
   return ; 
end     
%session = second(  datetime('now') ) * 1000 ; 
tablename = sprintf( 'image%d', round( rand()*1000000) ); 
%signatureData = cell2mat(signatureData) ; 
sql = sprintf( 'CREATE TABLE %s(figure varbinary(max))', tablename ) ;
execute(conn,sql);
% Insert images to the database table
T = table( {signatureData},'VariableNames',{'figure'}) ;
sqlwrite(conn, tablename , T );

sql = sprintf( 'UPDATE tuser SET signature = (select figure from %s) WHERE id=%d',  tablename, id ) ;
execute(conn,sql);
% Elimination of the temporary table
execute(conn, sprintf('DROP TABLE %s', tablename) ) ; 

end