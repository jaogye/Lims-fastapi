% This function updates the detail of specification in dspec table based on
% the intervals saved in spec for a given id (idspec)
function  sql = updatedSpec(conn, idspec, limits, tests)

sql = "DELETE FROM dspec WHERE spec_id=%s ; "; 
sql1 = sprintf(sql, string(idspec) ) ; 
execute(conn, sql1);
commit(conn) ; 

for i = 1:height(tests)
    min = limits{1,i}(1) ; 
    max = limits{1,i}(2) ; 
    if class(min) == "string" && class(max) == "string"
       if ismissing(min)
          min = "" ;  
       end 
       if ismissing(max)
          max = "" ;  
       end        
       if not ( strcmp(min, "") ) || not ( strcmp(max, "") )
          if strcmp(min,"Y") || strcmp(min,"X")
             min = ""; 
          end    
          sql = "INSERT dSpec(spec_id, variable_id, min, max) VALUES( %s, %s, '%s', '%s') ; "; 
          sql = sprintf(sql , [ idspec, string(tests{i,1}), min, max ]) ; 
          execute(conn, sql);   
       end
    end 
end % for

commit(conn) ; 
end 
