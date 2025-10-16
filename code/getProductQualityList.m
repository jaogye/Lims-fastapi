function [list, Variables] = getProductQualityList(conn, product)

ddate = datetime  ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdatefin = string( ddate )  ; 

ddate = datetime - 365 ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdateini = string( ddate )  ; 

product = strtrim(product) ; 
list = {} ; 
if strcmp(product, '')
   sql = "SELECT longname name FROM quality ; " ;     
else
   sql = "SELECT longname name FROM quality q, product p, spec s " + ...
    " WHERE s.typespec='GEN' and s.product_id=p.id and s.quality_id=q.id" + ...
    " and p.name='%s' and exists(SELECT * FROM sample ss, measurement m " + ...
    "WHERE ss.id = m.sample_id and  ss.product_id=p.id  and" + ...
    " ss.quality_id=q.id  and ss.date>='%s' and ss.date <='%s')" ;    
   sql = sprintf(sql, product, sdateini, sdatefin) ;       
end
T = select(conn, sql) ; 
if not( isempty(T) )
   list =  table2cell( table( T.name)) ; 
end

Variables = {} ; 
if strcmp(product, '')
   sql = "SELECT v.shortname name FROM variable v; " ;     
else
   sql = "SELECT v.shortname name FROM variable v " + ...
       " WHERE exists(SELECT * FROM product p, sample s, measurement m" + ...
       " WHERE s.id=m.sample_id and s.product_id=p.id and p.name='%s'" + ...
       " and s.date>='%s' and s.date <='%s' and m.variable_id=v.id)" ; 
   sql = sprintf(sql, product, sdateini, sdatefin) ;       
end
T = select(conn, sql) ; 
if not( isempty(T) )
   Variables =  table2cell(table( T.name)) ; 
end

end