% This function build a sql to insert into table spec
function  sql = getinsertspec(cols, reg ,limits, tests) 

sql = "INSERT into spec(" + cols{1,1} ;  
for i = 2:length(cols)  
    if not (ismissing( reg{1,i} ))
       sql = sql +"," + cols{1,i} ; 
    end
end

for i = 1:height(tests)  
    if not (ismissing( limits{1,i}(1)) ) 
       if tests.typevar(i) == "I" 
          sql = sql +"," + "min_" + tests.shortname(i) ; 
       else
          sql = sql +"," + tests.shortname(i) ;   
       end
    end
    if not (ismissing( limits{1,i}(2)) ) 
        if tests.typevar(i) == "I" 
           sql = sql +"," + "max_" + tests.shortname(i) ; 
        end  
    end

end % for


if strcmp( class(reg{1,1}), "double" ) || strcmp( class(reg{1,1}),  "int32") 
   sql = sql +") values( " + mat2str(reg{1,1}) ;
 else
   sql = sql +") values( '" + reg{1,1} + "'";
end      


for i = 2:length(reg)  
  if not (ismissing( reg{1,i} ))
    if strcmp( class(reg{1,i}), "double" )  || strcmp( class(reg{1,i}),  "int32") 
       sql = sql +", " + mat2str(reg{1,i}) ;
      else
       sql = sql +", '" + reg{1,i} + "'";
     end      
   end 
end

for i = 1:length(limits)  
    if not (ismissing( limits{1,i}(1)) )
       sql = sql +",'" + limits{1,i}(1)+"'"  ; 
    end
    if not (ismissing( limits{1,i}(2)) )
       if tests.typevar(i) == "I"  
          sql = sql +"," + "'" + limits{1,i}(2) + "'" ; 
       end
    end
end % for
sql = sql + ");" ; 

end 
