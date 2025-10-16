function [data] = readLogisticDatafromDB()
%% this function pulls data from logistic data base
% dsn less data source string for PVS data base
dsnless = "Driver={SQL Server Native Client 11.0}; Server=SRVPSQL01; Port=1433; Database=101; UID=matlab; PWD=Matlab2022.";
conn = odbc(dsnless);

% date 
datetoday=[datestr(now,'yyyy-mm-dd'),' 00:00:00.000'];

query1=['SELECT * ' ...
    'FROM "101".dbo.ns_Matlab WHERE date = ','''',datetoday,''''];


data = fetch(conn,query1);


end