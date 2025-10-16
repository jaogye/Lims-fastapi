function  data = getQualityList(conn) 

sql = "SELECT q.name from quality q ORDER BY q.name;" ; 

data = select (conn, sql) ; 
if height(data) > 0
   data.name = strtrim(data.name) ; 
end 
end 