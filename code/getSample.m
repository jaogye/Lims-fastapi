function sample  =  getSample(conn, sdate, typesample) 

if exist('typesample','var')
   sql = "select samplenumber SampleNumber, p.name Product, q.name Quality, sp.name SamplePoint, " + ...
    " loadingdate SampleDate, time SampleTime, remark Remark, createdby_id, samplepoint_id, " + ...
    " s.product_id, s.id, s.COA, s.Day_COA, s.COC  " + ...
    " FROM sample s left join samplepoint sp on s.samplepoint_id=sp.id, " + ...
    " product p, quality q  " + ...
    " WHERE s.product_id =p.id  and s.quality_id =q.id" + ...
    " and s.loadingdate = '%s' and s.typesample='%s' ;" ;  
   sql = sprintf(sql, [sdate, typesample]) ; 
else
   sql = "select samplenumber SampleNumber, p.name Product, q.name Quality, sp.name SamplePoint, " + ...
    " loadingdate SampleDate, time SampleTime, remark Remark, createdby_id, samplepoint_id, s.id, " + ...
    " s.product_id,  s.COA, s.Day_COA, s.COC  " + ...
    " FROM sample s left join samplepoint sp on s.samplepoint_id=sp.id, product p, quality q  " + ...
    "WHERE s.product_id =p.id and s.quality_id =q.id" + ...
    " and s.loadingdate = '%s' ;" ;      
   sql = sprintf(sql, sdate) ; 
 end

T = select (conn, sql ) ; 

sample = table(T.SampleNumber, T.Product, T.Quality, T.SamplePoint, ...
    T.SampleDate, T.SampleTime, T.Remark, T.COA, T.Day_COA, T.COC, T.id ) ;
sample.Properties.VariableNames{1} = 'SampleNumber' ; 
sample.Properties.VariableNames{2} = 'Product' ; 
sample.Properties.VariableNames{3} = 'Quality' ; 
sample.Properties.VariableNames{4} = 'SamplePoint' ; 
sample.Properties.VariableNames{5} = 'SampleDate' ; 
sample.Properties.VariableNames{6} = 'SampleTime' ; 
sample.Properties.VariableNames{7} = 'Remark' ; 
sample.Properties.VariableNames{8} = 'COA' ; 
sample.Properties.VariableNames{9} = 'Day_COA' ; 
sample.Properties.VariableNames{10} = 'COC' ; 
sample.Properties.VariableNames{11} = 'id' ;  
if height(sample) > 0
   sample.SampleNumber = strtrim( sample.SampleNumber ) ; 
   sample.Product = strtrim( sample.Product ) ; 
   sample.Quality = strtrim( sample.Quality ) ; 
   sample.SamplePoint = strtrim( sample.SamplePoint ) ; 
   sample.SampleDate = strtrim( sample.SampleDate ) ; 
   sample.SampleTime = strtrim( sample.SampleTime ) ; 
   sample.Remark = strtrim( sample.Remark ) ; 
end

end