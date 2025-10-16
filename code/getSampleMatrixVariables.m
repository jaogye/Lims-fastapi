% This function finds the position for spec table joined with other tables
function [indexCols, tests, msgerror] = getSampleMatrixVariables(conn, data) 

tests  = select( conn, "SELECT id, shortname, typevar FROM variable ORDER BY ord;" ) ; 
cols = data.Properties.VariableNames' ; 

indexCols = {} ; 
msgerror = {} ; 

for i = 1:height(tests)
    col = "has_" + tests{i,2}{1}; 
    index = -1 ;
    for j = 1:length(cols)
        if strcmpi( col , cols{j} )
           index = j ; 
           break ; 
        end    
    end     
    if index == -1
        msgerror{length(msgerror)+1} = sprintf("Column %s is not found in table SPEC", col) ;
        return 
    end        
    indexCols{i,1} = index ; 
end    

end