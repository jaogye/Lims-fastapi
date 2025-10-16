% This function is auxiliary and load logistic data from an excel file in
% data to the data table ns_matlab in 101
function  loadLogisticData(conn, data)

% This function load rows of logisticdata 
dt.date = "C" ; 
dt.time = "C" ;
dt.name_client = "C" ;
dt.ordernumber_PVS = "N" ; 
dt.article_no  = "N" ;
dt.ordernumber_client = "C" ; 
dt.description = "C" ; 
dt.loading_ton = "N" ;

for i=1:height(data)
    if isnan( data.ordernumber_client(i) )
       data.ordernumber_client(i) = 0 ;  
    end      


    column = data.Properties.VariableNames{1}  ; 
    sql =  "INSERT INTO ""101"".dbo.ns_matlab(" + column ; 
    for j = 2:width(data)
        column = data.Properties.VariableNames{j} ; 
        sql = sql + "," + column ; 
    end
    sql = sql + ") VALUES ('" + strtrim( data{i,1} ) + "'" ; 
    for j = 2:width(data)
        column = data.Properties.VariableNames{j}  ;
          if strcmp( getfield(dt, column), "C" )
             sql = sql + ", '" + strtrim( string(data{i,j}) ) + "'" ; 
            else
              value = strrep( strtrim( string( data{i,j})), ',','.') ; 
             sql = sql + ", " + value ; 
          end
    end
    sql = sql + ")"  ; 
    execute(conn, sql ) ; 
    commit(conn) ; 
end


end



