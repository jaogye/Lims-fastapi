% This function finds the position for spec table joined with other tables
function [indexCols, tests, msgerror] = getSpecVariables(conn, data) 

tests  = select( conn, "SELECT id, shortname, typevar FROM variable ORDER BY ord;" ) ; 
cols = data.Properties.VariableNames' ; 

indexCols = {} ; 
msgerror = {} ; 
for i = 1:height(tests)
    % This part finds the position of the min of the (I)nterval or the column
    % of a (L)ist test 
    if tests.typevar(i) == "I"
       colMin = [ 'min_' , tests{i,2}{1} ] ; 
    else       
       colMin =  tests{i,2}{1}; 
    end 
    indexMin = -1 ;
    for j = 1:length(cols)
        if strcmpi( colMin , cols{j} )
           indexMin = j ; 
           break ; 
        end    
    end     
    if indexMin == -1
        msgerror{length(msgerror)+1} = sprintf("Column %s is not found in table SPEC", colMin) ;
        return 
    end    
    
    indexMax = -1 ; 
    if tests.typevar(i) == "I"
      colMax = [ 'max_' , tests{i,2}{1} ] ;       
      for j = 1:length(cols)
          if strcmpi( colMax , cols{j} )
             indexMax = j ; 
             break ; 
          end    
      end     
      if indexMax == -1
          msgerror{length(msgerror)+1} = sprintf("Column %s is not found in table SPEC", colMax) ;
          return 
      end    
    end 
    indexCols{i,1} = indexMin ; 
    indexCols{i,2} = indexMax ; 
end    

return 