function data = getProduct(conn)
sql = "SELECT ' ' Action, name Name, bruto Bruto, Name_coa, id from product order by id;" ; 
data = select( conn, sql ) ;
end
