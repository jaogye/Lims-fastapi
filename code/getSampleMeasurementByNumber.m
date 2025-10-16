function [sample, measurement] = getSampleMeasurementByNumber(conn, samplenumber) 

sql = "SELECT  s.samplenumber SampleNumber,s.customer CustomerName, s.samplepoint Tank, s.article_no ArticleCode, " + ...
"concat(date,' ', time)  SampleDate, creationdate TestDate, p.name  Product, q.name Quality, s.remark Remark " + ...
" FROM sample s, product p, quality q " + ...
"WHERE samplenumber='%s' and s.product_id=p.id and s.quality_id=q.id  " + ...
" UNION SELECT s.samplenumber SampleNumber, 'PVS' CustomerName, s.samplepoint Tank, s.article_no ArticleCode, " + ...
" concat(date,' ', time)  SampleDate, creationdate TestDate, p.name  Product, q.name Quality, s.remark Remark  " + ...
" FROM sample s, product p, quality q " + ...
"WHERE samplenumber='%s' and s.product_id=p.id  and s.quality_id=q.id and s.client_id is null ; " ; 

sql = sprintf( sql, [samplenumber, samplenumber] ) ; 
sample = select( conn, sql ) ; 
sample.Remark = string(sample.Remark) ; 

sql = "SELECT s.samplenumber SampleNumber, m.*  FROM sample s, measurement m " + ...
" WHERE m.sample_id=s.id  and samplenumber='%s'; " ; 
sql = sprintf( sql, samplenumber ) ; 
measurement = select( conn, sql ) ; 

for i=1:height(measurement)
    if ismissing( measurement.value(i) )
       measurement.value(i) = 0 ; 
    end     
    if ismissing( measurement.min(i) )
       measurement.min(i) = - Inf ; 
    end     
    if ismissing( measurement.max(i) )
       measurement.max(i) = Inf ; 
    end     
end

end 