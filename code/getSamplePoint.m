function data = getSamplePoint(conn)
sql = "SELECT ' ' Action, name Name, id from SamplePoint order by name;" ; 
data = select( conn, sql ) ;
end
