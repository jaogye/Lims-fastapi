function measurement = getmeasurementRefresh(conn, SampleNumber)

sql = "SELECT s.samplenumber SampleNumber, m.*,  '' str_value, v.typevar, 0 modified " + ...
    " FROM sample s, measurement m, variable v " + ...
" WHERE m.variable_id=v.id and m.sample_id=s.id  and s.samplenumber='%s'" + ...
" ORDER BY  v.ord ; " ; 
sql = sprintf( sql, SampleNumber ) ; 
measurement = select( conn, sql ) ; 
measurement.SampleNumber = strtrim( string(measurement.SampleNumber) ); 
measurement.str_value = strtrim( string(measurement.str_value) ); 

for i=1:height(measurement)
    measurement.str_value(i) = string(measurement.value(i)) ; 
    if measurement.less(i) 
       measurement.str_value(i) = "<" + string(measurement.value(i)) ; 
    end 
    if measurement.value(i) == -1 || ismissing( measurement.value(i) )
       measurement.str_value(i) = "" ; 
    end     
    if ismissing( measurement.min(i) )
       measurement.min(i) = - Inf ; 
    end     
    if ismissing( measurement.max(i) )
       measurement.max(i) = Inf ; 
    end     
end
