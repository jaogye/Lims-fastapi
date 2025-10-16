% This function validates the column names of data table
function [ok, msg] = checkDataCols(data, cols)

ok = 1 ; 
msg = "" ; 
for i=1:length(cols)
    col1 =  string(data.Properties.VariableNames{i} ); 
    col2 =  string(cols{1,i})  ; 
    if not ( strcmpi( col1, col2  ))
       msg = "Incorrect order of columns. Expected column: " + cols{1,i} + " but it is received :" + data.Properties.VariableNames{i} ; 
       ok = 0 ;
       return 
    end
end
end
