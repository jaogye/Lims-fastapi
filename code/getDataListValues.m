% This function gets the values of listvalue tests involved in a given
% SampleNumber entered by the user
function listValues = getDataListValues(conn, SampleNumber) 

sql = "SELECT  l.id, v.shortname, l.variable_id, l.description " + ...
    " FROM variable v, listvalue l, measurement m, sample s  " + ...
    "WHERE l.variable_id = v.id and m.sample_id=s.id and v.typevar='L' and " + ...
    "m.variable_id=l.variable_id and s.samplenumber = '%s' ORDER BY v.id" ; 

sql = sprintf(sql, SampleNumber)  ; 
list  = select( conn, sql ) ; 

% Count the number of variables 
index = 1 ; 
ngrp = 0 ; 
while index <= height(list)
    variable_id = list.variable_id(index) ; 
    ngrp = ngrp + 1 ; 
    while index <= height(list) && variable_id == list.variable_id(index) 
       index = index + 1 ;          
    end    
end

index = 1 ; 
listValues = {}; 
while index <= height(list)
    variable_id = list.variable_id(index) ; 
    if ngrp > 1
      shortname = strtrim(list.shortname(index)) ;
      shortname = shortname{1} ; 
      if isempty(listValues)
         n=1;
      else
         n = length( { listValues{:,1} } ) + 1 ; 
      end
      listValues{n,1} = -1 ;  
      listValues{n,2} = ['-----' shortname ] ;     
    end 
    while index <= height(list) && variable_id == list.variable_id(index) 
       id = list.id(index) ;
       description = strtrim( list.description(index) ); 
       id = id(1) ; 
       des = description{1} ; 
       if isempty(listValues)
          n=1;
       else       
          n = length( { listValues{:,1} } ) + 1 ; 
       end
       listValues{n,1} = id ;  
       listValues{n,2} = des ; 
       index = index + 1 ;          
    end    
end

end