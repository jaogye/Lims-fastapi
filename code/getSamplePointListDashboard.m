function SamplePoint = getSamplePointListDashboard(conn, Product, Quality)

SamplePoint = {} ; 

ddate = datetime  ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdatefin = string( ddate )  ; 

ddate = datetime - 365 ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdateini = string( ddate )  ; 

if nargin == 1
   sql = "SELECT distinct sp.name FROM samplepoint sp, sample s, measurement m " + ...
    " WHERE s.id=m.sample_id and s.samplepoint_id=sp.id  and s.loadingdate>= '%s' and s.loadingdate <= '%s' ORDER BY sp.name"  ;   
   sql = sprintf(sql, sdateini, sdatefin) ;       
else
   sql = "SELECT distinct sp.name FROM samplepoint sp, sample s, product p, quality q, measurement m " + ...
    " WHERE  s.id=m.sample_id and s.samplepoint_id=sp.id  " + ...
    " and s.product_id=p.id and s.quality_id=q.id and s.loadingdate>= '%s' and s.loadingdate <= '%s' " + ...
    " and p.name='%s' and q.name='%s'  ORDER BY sp.name " ;
   sql = sprintf(sql, sdateini, sdatefin, Product, Quality) ;    
end

T = select(conn, sql) ; 
if not( isempty(T) )
   SamplePoint =  table2cell( table( T.name)) ; 
end

end