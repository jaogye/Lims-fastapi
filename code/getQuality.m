function data = getQuality(conn)
sql = "SELECT ' ' Action, name Name, longname LongName, id from quality order by id;" ; 
data = select( conn, sql ) ;
end
