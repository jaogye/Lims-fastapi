% This function computes the sql string to delete all rows of table Spec without interval in the variables 
function  sql = getdeletespec(limits, varnames) 

sql = "DELETE spec WHERE min_" + varnames{1,1} + " is NULL AND max_" + varnames{1,1} + " is NULL";  

for i = 2:length(varnames)  
    sql = sql +" AND " + "min_" + varnames{1,i} + " is ";
    sql = sql + "NULL" ; 

    sql = sql +" AND " + "max_" + varnames{1,i} + " is " ; 
    sql = sql + "NULL" ; 
end % for
sql = sql + ";" ;

end 