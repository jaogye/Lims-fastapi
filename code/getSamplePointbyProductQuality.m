function [msgerror, SamplePoint] = getSamplePointbyProductQuality(conn, Product, Quality)

msgerror = {} ; 
SamplePoint = table() ; 
Product = string( strtrim( Product ) ); 
Quality = string( strtrim( Quality ) ); 
sql = "SELECT x.SamplePoint from SampleMatrix x, product p, quality q " + ...
    " WHERE x.product_id=p.id AND  p.name='%s' AND x.quality_id=q.id AND  q.name='%s' ;" ; 

sql = sprintf(sql, [Product, Quality]) ; 
T = select(conn, sql) ; 
if not( isempty(T) )
   SamplePoint = T ; 
   SamplePoint.SamplePoint = strtrim( SamplePoint.SamplePoint ) ; 
else
    msgerror{1} = "(Product,Quality) :(" + Product+","+Quality + ") not found in SampleMatrix table.";    
end

end