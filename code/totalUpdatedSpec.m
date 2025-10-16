% This function updates all detail of specification table in dspec table based on
% the intervals saved in spec for each row in spec
function msgerror = totalUpdatedSpec(conn )

[indexCols, tests, msgerror] = getSpecVariables(conn) ; 

data = select(conn, "SELECT * FROM spec ") ; 

for i = 1:height(data)
    disp(i) ; 
    idspec = data.id(i) ; 
    sql = "DELETE FROM dspec WHERE spec_id=%s ; "; 
    sql1 = sprintf(sql, string(idspec) ) ; 
    execute(conn, sql1);
    commit(conn) ; 
    
    for j = 1:height(tests)        
        test = string( tests{j,2} ); 
        minValue = data{i, indexCols{j,1} } ;
        disp(num2str(i) + " " + num2str(j) )
        smin="null" ; 
        if not (isnan( minValue) ) && minValue > 0  
           smin = mat2str( minValue ) ; 
        end
        maxValue = data{i, indexCols{j,2} } ;
        smax = "null" ; 
        if not (isnan( maxValue ) ) && maxValue > 0
           smax = mat2str( maxValue ) ;         
        end

        if not(isnan(minValue)) || not(isnan(maxValue)) || (minValue<0 && maxValue<0)
           sql = "INSERT dSpec(spec_id, variable_id, min, max) VALUES( %s, %s, %s, %s) ; "; 
           sql = sprintf(sql , [ idspec, string(tests{j,1}), smin, smax ]) ; 
           execute(conn, sql);   
           commit(conn) ; 
        end
    end       
end % for




end



