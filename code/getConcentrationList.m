function [list, Variables] = getConcentrationList(conn, bruto)

ddate = datetime  ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdatefin = string( ddate )  ; 

ddate = datetime - 365 ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdateini = string( ddate )  ; 

bruto = strtrim(bruto) ; 

list = {} ; 
if strcmp(bruto, '')
   sql = "SELECT distinct p.name FROM product p, sample s, measurement m  WHERE " + ...
    " s.id=m.sample_id and s.product_id=p.id and  s.date>='%s' and s.date<='%s' " ; 
   sql = sprintf(sql, sdateini, sdatefin) ;
   
else
   sql = "SELECT distinct p.name FROM product p, sample s, measurement m  WHERE " + ...
    "  s.id=m.sample_id and replace( replace(bruto, '<sub>', ''), '</sub>', '')='%s'" + ...
    "  and s.product_id=p.id and  s.date>='%s' and s.date<='%s' " ; 
   sql = sprintf(sql, bruto, sdateini, sdatefin) ;
end
T = select(conn, sql) ; 
if not( isempty(T) )
   list =  table2cell( table( T.name)) ; 
end

Variables = {} ; 
if strcmp(bruto, '')
   sql = "SELECT shortname name FROM variable ; " ;     
else
  sql = "SELECT v.shortname name FROM variable v WHERE " + ...
  " exists(SELECT * FROM sample s, measurement m, product p " + ...
  " WHERE s.id =m.sample_id and " + ...
  " replace( replace(bruto, '<sub>', ''), '</sub>', '')='%s'" + ...
  " and s.date>='%s' and s.date<='%s' and s.product_id=p.id" + ...
  " and m.variable_id=v.id  )" ; 
  sql = sprintf(sql, bruto, sdateini, sdatefin) ;
end
T = select(conn, sql) ; 
if not( isempty(T) )
   Variables =  table2cell( table( T.name)) ; 
end

end