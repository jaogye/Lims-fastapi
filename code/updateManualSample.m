function [idsample, msgerror] = updateManualSample(conn, sample, measurement)

msgerror = {} ;  
dt = datetime ; 
dt.Format='yyyy-MM-dd hh:mm::ss' ; 
sdt = string(dt) ; 
idproduct = sample.idproduct(1) ;
idquality = sample.idquality(1) ;
SamplePoint = strtrim( string( sample.SamplePoint(1) )); 
idSamplePoint = checkFK( conn, "SELECT id FROM samplepoint WHERE name='%s'", SamplePoint ) ; 

%idspec = checkFK(conn, "SELECT id FROM spec where typespec='GEN' and product_id=%d  and quality_id=%d;", [idproduct, idquality] ) ; 

[idspec, ~ ] = getSpecId(conn, idproduct, idquality, "") ; 

if strcmp( sample.Action(1) , "I" )
   sql = "INSERT INTO Sample(TypeSample, SampleNumber, Product_id, Quality_id, " + ...
       "Spec_id, SamplePoint_id, Createdby_id, creationdate, " + ...
       "loadingdate, time, Remark, article_no ) " + ...
       "VALUES ('MAN','%s', %s, %s,   %s, %s, %s, '%s', '%s', '%s', '%s', 0) ; " ; 
   
   values = [ sample.SampleNumber(1), sample.idproduct(1), sample.idquality(1), idspec, ...
        idSamplePoint, sample.iduser(1), sdt, sample.ssdate(1),... 
       sample.stime(1), sample.Remark(1) ] ; 
   sql = sprintf(sql, values ) ; 
   execute(conn, sql); 
   T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
   idsample = T.x(1) ; 
end 

if strcmp( sample.Action(1) , "U" )
 sql = "UPDATE Sample SET Product_id=%s, Quality_id=%s, Spec_id=%s, " + ...
     "SamplePoint_id=%s, loadingdate='%s', time='%s', Remark='%s' WHERE id=%s" ; 

 values = [sample.idproduct(1), sample.idquality(1), idspec, ...
     idSamplePoint, sample.ssdate(1), sample.stime(1), ...
     sample.Remark(1), sample.id(1)]; 
 sql = sprintf( sql, values ) ;  
 execute(conn, sql); 
 idsample = sample.id(1) ; 
 sql = sprintf("DELETE FROM measurement WHERE sample_id=%d", idsample) ; 
 execute(conn, sql); 
end 

% Insert of measument limits 
for j=1:height(measurement) 
    if not( measurement.Flag(j) )
       continue ; 
    end    
    variable = measurement.Variable(j) ; 
    variable_id = measurement.variable_id(j) ; 
    min = measurement.Min(j) ; 
    min = string( strtrim(min{1}) ); 
    max = measurement.Max(j) ; 
    max = string( strtrim(max{1}) ); 
    %if measurement{j,2}
    if min == ""
       min = "NULL" ; 
    end    
    if max == ""
       max = "NULL" ; 
    end            
    sql = "INSERT INTO Measurement(sample_id, variable_id, variable, min, max, value ) " + ...
           "VALUES (%d, %d, '%s', '%s', '%s',-1) " ; 
    sql = sprintf(sql, idsample, variable_id, string(variable) , min, max ) ; 
    execute(conn, sql) ;
    %end 
end

commit(conn) ; 
end
