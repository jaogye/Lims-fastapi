% This function is used in the dashboard
function [Bruto, Variables] = getProductBrutoList(conn, SamplePoint)

ddate = datetime  ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdatefin = string( ddate )  ; 

ddate = datetime - 365 ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdateini = string( ddate )  ; 
Bruto = {} ; 

if strcmp( SamplePoint, '')
   sql = "SELECT distinct replace( replace(bruto, '<sub>', ''), '</sub>', '') name " + ...
       " FROM product p, sample s, measurement  m  WHERE  " + ...
       " s.id=m.sample_id and s.product_id=p.id " + ...
       " and s.loadingdate>= '%s' and s.loadingdate <= '%s'" ; 
   sql = sprintf(sql, sdateini, sdatefin ) ; 

   sql2 = "SELECT distinct  v.shortname name  FROM variable v, sample s, " + ...
       " measurement m, product p  WHERE s.id=m.sample_id and s.product_id=p.id and m.variable_id=v.id   " + ...
    " and s.loadingdate>= '%s' and s.loadingdate <= '%s'" ; 
   sql2 = sprintf(sql2, sdateini, sdatefin ) ; 

else
   sql = "SELECT distinct replace( replace(bruto, '<sub>', ''), '</sub>', '') name " + ...
       " FROM product p, sample s, measurement m, samplepoint sp  WHERE  " + ...
       " s.id=m.sample_id and s.product_id=p.id " + ...
       " and s.loadingdate>= '%s' and s.loadingdate <= '%s' and s.samplepoint_id=sp.id and sp.name='%s'" ; 
    
   sql = sprintf(sql, sdateini, sdatefin, SamplePoint ) ; 

   sql2 = "SELECT distinct  v.shortname name  FROM variable v, sample s, " + ...
       " measurement m, product p, samplepoint sp  WHERE s.id=m.sample_id and " + ...
       "s.product_id=p.id and m.variable_id=v.id   " + ...
    " and s.loadingdate>= '%s' and s.loadingdate <= '%s'  and s.samplepoint_id=sp.id and sp.name='%s'" ; 
   
   sql2 = sprintf(sql2, sdateini, sdatefin, SamplePoint ) ;    
end

T = select(conn, sql) ; 
if not( isempty(T) )
   Bruto = strtrim( table2cell( table( T.name)) ); 
   if length( Bruto) > 1 
      Bruto{length(Bruto)+1} = '' ;    
   end 
end

Variables = {} ; 
T = select(conn, sql2) ; 
if not( isempty(T) )
   Variables = strtrim( table2cell( table( T.name)) ); 
end

end