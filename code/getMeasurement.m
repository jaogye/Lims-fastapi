function measurement  =  getMeasurement(conn, idsample) 

 sql = "SELECT variable, 1 flag FROM measurement WHERE id=%d;" + ...
     "UNION SELECT " ;      
    sql = sprintf(sql, idsample) ; 
T = select (conn, sql ) ; 

measurement = table(T.variable, T.Product, T.Quality, T.measurementPoint, T.measurementDate, T.measurementTime, T.Remark, T.id) ;
measurement.Properties.VariableNames{1} = 'measurementNumber' ; 
measurement.Properties.VariableNames{2} = 'Product' ; 
measurement.Properties.VariableNames{3} = 'Quality' ; 
measurement.Properties.VariableNames{4} = 'measurementPoint' ; 
measurement.Properties.VariableNames{5} = 'measurementDate' ; 
measurement.Properties.VariableNames{6} = 'measurementTime' ; 
measurement.Properties.VariableNames{7} = 'Remark' ; 
measurement.Properties.VariableNames{8} = 'id' ;  
if height(measurement) > 0
   measurement.measurementNumber = strtrim( measurement.measurementNumber ) ; 
   measurement.Product = strtrim( measurement.Product ) ; 
   measurement.Quality = strtrim( measurement.Quality ) ; 
   measurement.measurementPoint = strtrim( measurement.measurementPoint ) ; 
   measurement.measurementDate = strtrim( measurement.measurementDate ) ; 
   measurement.measurementTime = strtrim( measurement.measurementTime ) ; 
   measurement.Remark = strtrim( measurement.Remark ) ; 
end

end