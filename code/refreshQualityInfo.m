% This function refresh the quality info table from LabInput option 
% The function update table measurement of a generated sample with new
% information  of samplematrix 
function refreshQualityInfo(conn, SampleNumber)  

typesample = string ( extractBetween(SampleNumber,1,1) ); 
sql = "SELECT id, spec_id, product_id, quality_id, samplematrix_id, customer " + ...
    "FROM sample WHERE samplenumber='%s'" ; 
sql = sprintf( sql, SampleNumber ) ; 

T = select(conn, sql) ; 
idSample = T.id(1) ; 
idSampleMatrix = T.samplematrix_id(1) ; 
%idSpec = T.spec_id(1) ; 
idproduct = T.product_id(1) ;  
idquality = T.quality_id(1) ; 
customer = T.customer(1) ; 
[idSpec, ~ ] = getSpecId(conn, idproduct, idquality, customer)  ; 

switch typesample
  case "C"    
    %if strcmp(certificaat, 'N')
       idsample = checkFK(conn, "SELECT id FROM sample WHERE samplenumber='%s'", SampleNumber) ;  
       sdelete = "DELETE FROM measurement WHERE sample_id=%d" ; 
       sdelete = sprintf( sdelete,  idsample ) ; 
       execute(conn, sdelete) ;    
    %end
    intervals = getCustomerQualityInfo(conn, idSpec ) ; 

  case "P"
    intervals = getProductionQualityInfo(conn, idSampleMatrix) ; 

end

for i=1:height(intervals)
    if ismissing( intervals.min(i) )
       intervals.min(i) = {''} ; 
    end     
    if ismissing( intervals.max(i) )
       intervals.max(i) = {''} ; 
    end     
end

% Deleting the previous Quality info 
sql = "DELETE FROM measurement WHERE sample_id=%d " ; 
sql = sprintf(sql, idSample) ; 
execute(conn, sql) ; 
insertmeasurement(conn, idSample, intervals) ; 
commit(conn) ;     

%sql = "SELECT s.samplenumber SampleNumber, m.*,  '' str_value, v.typevar, 0 modified " + ...
%    " FROM sample s, measurement m, variable v " + ...
%" WHERE m.variable_id=v.id and m.sample_id=s.id  and s.samplenumber='%s'; " ; 
%sql = sprintf( sql, SampleNumber ) ; 
%QualityInfo = select( conn, sql ) ; 

end 

function intervals = getProductionQualityInfo(conn, idSampleMatrix)

% Selecting the new information of samplematrix
sql = "SELECT v.shortname variable, null min, null max, d.variable_id   " + ...
        " FROM dsamplematrix d, variable v  " + ...
        " WHERE d.variable_id=v.id and d.samplematrix_id =%s " + ...
        " and not exists(SELECT * FROM dspec d2, samplematrix sm, spec sp" + ...
        " WHERE sm.product_id=sp.product_id and sm.quality_id=sp.quality_id and sp.typeSpec='GEN'" + ...
        " and d.variable_id = d2.variable_id)  " + ...
        "UNION " + ...
        "SELECT v.shortname variable, min, max,  d.variable_id  " + ...
        " FROM dsamplematrix d, variable v, dspec d2, samplematrix sm, spec sp " + ...
        " WHERE d.variable_id=v.id and d.samplematrix_id =%s and sp.typeSpec='GEN' " + ...
        " and d.samplematrix_id=sm.id and d2.spec_id=sp.id " + ...
        " and sm.product_id=sp.product_id and sm.quality_id=sp.quality_id " + ...
        " and d.variable_id = d2.variable_id; ";

sql = sprintf(sql, idSampleMatrix, idSampleMatrix) ; 
intervals = select(conn, sql ); 

end 

function intervals = getCustomerQualityInfo(conn, idSpec)

% Selecting the new information of samplematrix
sql =   "SELECT v.shortname variable, d.variable_id, min, max, '' listvalue " + ...
        " FROM dspec d, variable v " + ...
        " WHERE d.variable_id=v.id and d.spec_id = %d ";

sql = sprintf(sql, idSpec ) ; 
intervals = select(conn, sql ); 

end