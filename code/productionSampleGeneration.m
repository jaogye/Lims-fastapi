% This function generated fake samples in order to test the dashboard
function productionSampleGeneration()
inidate = datetime(2022,6,1) ;  
conn = getconn() ; 
iduser = 1 ; 

for offset=0:240
    ddate = inidate + offset ;  
    ddate.Format = 'yyyy-MM-dd' ; 
    sdate = string( ddate )  ; 
    disp(sdate)  
    loadCustomerSample(conn, sdate , 1) ;
    loadProductionSample(conn, sdate, iduser)   ;    
    commit(conn) ;
end

%execute(conn, "delete from measurement where min is null and max is null") ; 
T = select(conn, "select * from measurement where min is not null or max is not null") ; 

for i=1:height(T)
    n1 = T.min(i) ; 
    if isnan( T.min(i) ) 
      n1 = T.max(i) / 2 ;      
    end 
    n2 = T.max(i) ; 
    if isnan( T.max(i) ) 
      n2 = T.min(i) + 2 ;      
    end     
    rvalue = n1+ rand*(n2-n1) ; 
    if mod(i,100) ==0
       %percentaje = 100 * i /height(T)  ; 
       %disp(percentaje) ; 
    end 
    idSample = T.sample_id(i) ; 
    idVariable = T.variable_id(i) ; 
    execute(conn, sprintf( "UPDATE measurement SET value = %d WHERE " + ...
        " sample_id=%d and variable_id=%d", rvalue, idSample, idVariable) ) ;    
    commit(conn) ; 
end  

end 