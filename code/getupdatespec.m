% This function build a sql to update table spec
function  sql = getupdatespec(id, cols, reg ,limits, tests) 

sql = "UPDATE spec SET " + cols{1,1} + "=";  
if strcmp( class(reg{1,1}), "double" ) 
   sql = sql + mat2str(reg{1,1}) ;
 else
   sql = sql + "'" + reg{1,1} + "'";
end      

for i = 2:length(cols)  
    sql = sql +"," + cols{1,i} + "=";
    if ismissing( reg{1,i} ) 
       sql = sql + "NULL" ; 
     else      
      if strcmp( class(reg{1,i}), "double" ) || strcmp( class(reg{1,i}),  "int32") 
         sql = sql + mat2str(reg{1,i}) ;
       else
         sql = sql + "'" + reg{1,i} + "'";
      end      
    end
end % for

for i = 1:height(tests)  
    if tests.typevar(i) == "I"
       sql = sql +"," + "min_" + tests.shortname(i) + "=";
    else
       sql = sql +"," + tests.shortname(i) + "="; 
    end
    if ismissing( limits{1,i}(1)) 
       sql = sql + "NULL" ; 
    else
       sql = sql + "'" + limits{1,i}(1) + "'" ;  
    end
    if tests.typevar(i) == "I"
       sql = sql +"," + "max_" + tests.shortname(i) + "=" ; 
       if ismissing( limits{1,i}(2))
          sql = sql + "NULL" ; 
       else 
          sql = sql + "'" + limits{1,i}(2) + "'" ;  
       end
    end
end % f3or

sql = sql + " WHERE id = " + id + ";" ;

end 

