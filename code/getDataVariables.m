% This function gets the column positions of  tests in the excel sheet
% entered by the user
function [indexCols, tests, msgerror] = getDataVariables(conn, data, msgerror) 

tests  = select( conn, "SELECT id, shortname, typevar FROM variable ORDER BY ord;" ) ; 
cols = data.Properties.VariableNames' ; 

indexCols = {} ; 
for i = 1:height(tests)
    col =  tests{i,2}{1}  ; 
    index = -1 ;
    for j = 1:length(cols)
        if strcmp( col , cols{j} )
           index = j ; 
           break ; 
        end    
    end     
    if index == -1
       msgerror{length(msgerror)+1} = sprintf("Column %s not found in user excel Data", col) ;      
       return 
    end        
    indexCols{i} = index ; 
end    

return 

end