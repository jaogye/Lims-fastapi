function data = getVariable(conn)

sql = "SELECT ' ' Action,  shortname Shortname, test Test, " + ...
    "element Element, unit Unit, ord Ord, TypeVar, '' listvalue, id"+ ...
 " FROM variable ORDER BY ord,id;" ; 

data = select( conn, sql ) ; 
for i=1:height(data)    
    id = data.id(i) ; 
    if data.TypeVar(i) == "L"
       T = select(conn, sprintf("SELECT description FROM listvalue WHERE variable_id= %d" , id  ) ) ; 
       listvalue = strtrim(string(T.description(1) )) ;
       for j=2:height(T) 
           listvalue = listvalue + ", " + strtrim(string(T.description(j) )) ;
       end
       data.listvalue(i) = {listvalue} ; 
    end    
end
%data = table( d.Action, d.shortname, d.test, d.element, d.unit, d.id ) ;
%data.Properties.VariableNames{1} = 'Action' ; 
%data.Properties.VariableNames{2} = 'Shortname' ; 
%data.Properties.VariableNames{3} = 'Test' ; 
%data.Properties.VariableNames{4} = 'Element' ; 
%data.Properties.VariableNames{5} = 'Unit' ; 
%data.Properties.VariableNames{6} = 'id' ; 

end
