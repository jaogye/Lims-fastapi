function SamplePoint = getSamplePointList(conn, Product, Quality)

SamplePoint = {} ; 

if nargin == 1
   sql = "SELECT sp.name FROM samplepoint sp  ORDER BY sp.name"  ;   
else
   sql = "SELECT distinct sp.name FROM samplepoint sp, samplematrix sm, product p, quality q " + ...
    " WHERE  sm.samplepoint_id=sp.id  " + ...
    " and sm.product_id=p.id and sm.quality_id=q.id  " + ...
    " and p.name='%s' and q.name='%s'  ORDER BY sp.name " ;
   sql = sprintf(sql, Product, Quality) ;    
end

T = select(conn, sql) ; 
if not( isempty(T) )
   SamplePoint =  table2cell( table( T.name)) ; 
end

end