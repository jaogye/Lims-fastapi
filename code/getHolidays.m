function data = getHolidays(conn)

sql = "SELECT ' ' Action, date, description, id from holidays order by date ;" ; 

d = select( conn, sql ) ;
data = table( d.Action, d.date, d.description, d.id ) ;
data.Properties.VariableNames{1} = 'Action' ; 
data.Properties.VariableNames{2} = 'Date' ; 
data.Properties.VariableNames{3} = 'Description' ; 
data.Properties.VariableNames{4} = 'id' ; 

end
