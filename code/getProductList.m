function  data = getProductList(conn) 

sql = "SELECT p.name from product p ORDER BY p.name;" ; 

data = select (conn, sql) ; 
if height(data) >0
   data.name = strtrim(data.name) ; 
end 
end 