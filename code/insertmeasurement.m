function  insertmeasurement(conn, idsample, limits) 


 for j=1:height(limits) 
       variable = string(limits.variable(j) ); 
       variable_id = limits.variable_id(j) ; 
       min = limits.min(j) ;
       min = strtrim( min{1}) ; 
       if isempty(min) || str2double(min) < 0
           min = "NULL" ; 
       end    
       max = limits.max(j); 
       max = strtrim( max{1} ); 
       if isempty(max)  || str2double(max) < 0 
           max = "NULL" ; 
       end    
       sInsert = "INSERT INTO Measurement(sample_id, variable_id, variable, min, max, value ) " + ...
               "VALUES (%d, %d, '%s', '%s', '%s', -1)" ; 
       
       sInsert = sprintf( sInsert , idsample, variable_id, variable, min, max  ) ; 
       execute(conn, sInsert) ;       
end

end