% This function gets the id from spec satisfying idproduct and idquality
% and customer 
function [idspec, certificaat ] = getSpecId(conn, idproduct, idquality, customer)    
certificaat = "9999" ; 
idspec = 0 ; 
idproduct = string(idproduct) ;
idquality = string(idquality) ; 
% I seek specifications whit certificaat='Y'
sql = "SELECT * FROM spec WHERE typespec='CLI' and product_id=%s and quality_id=%s and customer='%s'; " ; 
sql = sprintf( sql ,  [idproduct , idquality, customer] ) ;
T= select(conn, sql) ; 
if height(T) > 0
   idspec = T.id ;       
   certificaat = strtrim( T.certificaat(1)) ; 
  else
   sql = "SELECT * FROM spec WHERE typespec='GEN' and product_id=%s and quality_id=%s ; " ; 
   sql = sprintf( sql , [idproduct, idquality] ) ;
   T = select(conn, sql) ; 
   if height(T) > 0
      idspec = T.id ;   
   end 
end
end


function limits = getvariablelimits(T, inivariable, finvariable) 

offset = finvariable - inivariable + 1;
limits = {} ; 
k=0 ; 
for j=inivariable:finvariable
    str = T.Properties.VariableNames{j}; 
    name = extractBetween(str,5, length(str) ) ;  
    if not(isnan( T{1,j}) ) || not( isnan( T{1,j+offset}) )
       k=k+1; 
       limits{k} = {name,  T{1,j}, T{1,j+offset} }  ;
    end   
end
end