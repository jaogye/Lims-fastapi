% This function extracts the interval of a given variable for
% idProduct and idQuality
function  Intervals = getVariableInterval(conn,  Variable, bruto, idProduct, idQuality) 

mmin = -inf ; mmax = inf ;  
Intervals = table(mmin, mmax) ; 
if ismissing( Variable ) 
   return
end 
Variable = strtrim( Variable) ; 

scol1 = "min(s.min_"+string(Variable) +") mmin" ; 
scol2 = "min(s.max_"+string(Variable) +") mmax" ; 
sFrom = "spec s" ; 
sWhere1 = "s.typespec='GEN' and s.min_" + Variable + " is not null " ;
sWhere2 = "s.typespec='GEN' and s.max_" + Variable + " is not null " ;

if not(strcmp(bruto, '') )
   sFrom = sFrom + ", product p " ; 
   sWhere1 = sWhere1 + " and s.product_id = p.id " + ...
    " and replace( replace(p.bruto, '<sub>', ''), '</sub>', '')='"+strtrim(bruto)+"' " ; 
   sWhere2 = sWhere2 + " and s.product_id = p.id " + ...
    " and replace( replace(p.bruto, '<sub>', ''), '</sub>', '')='"+strtrim(bruto)+"' " ; 
   
end
if idProduct > 0
   sWhere1 = sWhere1 + " and s.product_id=" + string(idProduct) ; 
   sWhere2 = sWhere2 + " and s.product_id=" + string(idProduct) ; 
end

if idQuality > 0
   sWhere1 = sWhere1 + " and s.quality_id=" + string(idQuality) ; 
   sWhere2 = sWhere2 + " and s.quality_id=" + string(idQuality) ; 
end
sql1 = "SELECT " + scol1 + " FROM " + sFrom + " WHERE " + sWhere1 ; 
sql2 = "SELECT " + scol2 + " FROM " + sFrom + " WHERE " + sWhere2 ; 

T1 = select(conn, sql1) ; 
T2 = select(conn, sql2) ; 
if height(T1) >0 && strcmp( strtrim(T1.mmin), '') > 0
   Intervals.mmin = str2double(T1.mmin);  
end

if height(T2) >0 && strcmp( strtrim(T2.mmax), '') > 0 
   Intervals.mmax = str2double(T2.mmax) ;  
end     

end

