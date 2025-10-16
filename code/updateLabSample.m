% This function updates the lab input into the database
function  ok = updateLabSample(conn, tsample, tmeasurement, iduser ) 
ok = 1 ; 
for i=1:height(tsample)
   samplenumber = strtrim( tsample.SampleNumber(i) ); 
   SamplePoint = strtrim( string( tsample.Tank(i) ) ); 
   idSamplePoint = checkFK( conn, "SELECT id FROM samplepoint WHERE name='%s'", SamplePoint ) ; 
   Remark = strtrim( tsample.Remark(i)) ; 
   BatchNumber = strtrim( tsample.batchnumber(i) );
   ContainerNumber = strtrim( tsample.containernumber(i) );
   n = strlength(Remark) ; 
   Remark = extractBefore(Remark,n+1) ;    
   stestdate = tsample.testdate(i) ; 
   if ismissing( stestdate ) || isempty( stestdate )
      stestdate = "" ; 
   end     
   if idSamplePoint == 0
      sql = "UPDATE sample SET remark='%s', batchnumber='%s', " + ...
          "containernumber='%s', testdate='%s' WHERE samplenumber='%s' ;" ; 
      sql = sprintf(sql, [ Remark, BatchNumber, ContainerNumber, stestdate, samplenumber]) ; 
   else
      sql = "UPDATE sample SET SamplePoint_id=%s, remark='%s', batchnumber='%s', " + ...
          "containernumber='%s' , testdate='%s' WHERE samplenumber='%s' ;" ; 
      sql = sprintf(sql, [idSamplePoint, Remark, BatchNumber, ContainerNumber, stestdate, samplenumber]) ; 
   end 
   execute( conn, sql ) ; 
%   sql2 = sprintf("SELECT testdate FROM sample WHERE SampleNumber = '%s'", samplenumber ) ;   
%   T = select(conn, sql2 )  ;  
%   if ismissing(T.testdate(1) ) || isempty(T.testdate(1))
%      updateS = "UPDATE sample set testdate='' WHERE samplenumber='%s' " ; 
%      sql = sprintf(updateS, samplenumber ) ; 
%      execute(conn,sql) ;  
%   end 
   commit(conn) ;    
end

updateM = "UPDATE measurement SET value=%s, testedby_id=%d, testdate='%s', less=%d, " + ...
    "listvalue='%s', listvalue_id=%s WHERE sample_id=%d and variable_id=%d  ;" ;   
for j=1:height(tmeasurement)
       %variable = strtrim(tmeasurement.variable(j)) ; 
       variable_id = tmeasurement.variable_id(j) ; 
       value = mat2str( tmeasurement.value(j) ) ; 
       idsample = tmeasurement.sample_id(j) ;         
       %modified = tmeasurement.modified(j) ;         
       listvalue = tmeasurement.listvalue(j) ;
       listvalue_id = tmeasurement.listvalue_id(j) ;
       testdate = tmeasurement.testdate(j) ;
       if listvalue_id < 0
          listvalue_id = "NULL"  ; 
       else   
          listvalue_id = string(listvalue_id) ;  
       end     
       less = 0 ; 
       if tmeasurement.less(j)
          less = 1 ; 
       end    
       sql = sprintf(updateM,  value, iduser, testdate{1}, less, listvalue{1}, listvalue_id,  idsample,  variable_id ) ; 
       execute(conn,sql) ; 
end

end