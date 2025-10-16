function msgerror = loadProductionSample(conn, sdate, iduser)

typesample = "PRO" ; 
date0 = datetime( sdate,'InputFormat','yyyy-MM-dd') ; 
msgerror = {'*********Error Messages of Production SampleMatrix******'} ; 
Owner = "PVS" ; 
%sql = "SELECT * FROM sample WHERE typesample='PRO' and  date='%s' ;" ; 
%sql = sprintf(sql, sdate ) ;
%T = select(conn, sql) ;
%if not(isempty(T))   
%   return ;  
%end    
inidate = getFirstday(conn, date0, '1/2 year') ; 
if strcmp( inidate , sdate )
   msgerror2 = loadProductionSampleFrequency(conn, sdate, '1/2 year', iduser, "1/2 year sample", Owner, typesample) ;  
   msgerror = [msgerror, msgerror2] ;  
end

inidate = getFirstday(conn, date0, 'Week') ; 
if strcmp( inidate , sdate )
   msgerror2 = loadProductionSampleFrequency(conn, sdate, 'Week', iduser, "Weekly sample", Owner, typesample) ;  
   msgerror = [msgerror, msgerror2] ;  
end

inidate = getFirstday(conn, date0, 'Month') ; 
if strcmp( inidate , sdate )
   msgerror2 = loadProductionSampleFrequency(conn, sdate, 'Month', iduser, "Montly sample", Owner, typesample) ;  
   msgerror = [msgerror, msgerror2] ;  
end

inidate = getFirstday(conn, date0, 'Quarter') ; 
if strcmp( inidate , sdate )
   msgerror2 = loadProductionSampleFrequency(conn, sdate, 'Quarter', iduser, "Quarterly sample", Owner, typesample) ;  
   msgerror = [msgerror, msgerror2] ;  
end
msgerror2 = loadProductionSampleFrequency(conn, sdate, 'Day', iduser, "Daily sample", Owner, typesample) ;  
msgerror = [msgerror, msgerror2] ;  
if length(msgerror) == 1
   msgerror = {} ; 
end

end

function msgerror = loadProductionSampleFrequency(conn, sdate, Frequency, iduser, Description, Owner, typesample) 

msgerror = {} ; 
sql = "SELECT x.*, p.name Product, q.name Quality, sp.name SamplePoint " + ...
    "FROM Samplematrix x, product p, quality q, samplepoint sp " + ...
    "WHERE Frequency='%s' and x.product_id=p.id and x.quality_id=q.id and " + ...
    " x.samplepoint_id=sp.id and " + ... 
" not exists(SELECT * FROM sample s where typesample='%s' and s.loadingdate='%s' and x.product_id=s.product_id); ";
sql = sprintf(sql, Frequency, sdate, typesample);
T = select(conn, sql) ;
%disp("loadProductionSample " + string(Frequency) + " " + string( height(T) ) ) ;
dd = datetime('06:00','InputFormat','HH:mm') ;
for i=1:height(T)
    dd = dd + minutes(1) ;
    stime = datestr(dd,'HH:MM' ) ; 
    msgerror2 = insertsample(conn, T, i, iduser, sdate, Description, Owner, typesample, stime) ; 
    msgerror = [msgerror, msgerror2] ;  
end     
commit(conn) ; 
end

                
function msgerror = insertsample(conn, T, i, iduser, sdate, Description, Owner, typesample, stime )

    idproduct = string(T.product_id(i) );     
    idquality = string(T.quality_id(i) );  
    Product = strtrim( string(T.Product(i) ));
    Quality = strtrim( string(T.Quality(i)) ); 
    Frequency = strtrim( string(T.Frequency(i)) ); 
    SamplePoint = strtrim( string(T.SamplePoint(i) )); 
    idSampleMatrix = string(T.id(i) );     
    idSamplePoint = string(T.SamplePoint_id(i) ) ;
    msgerror = {} ; 
    dt = datetime ; 
    dt.Format = 'yyyy-MM-dd HH:mm:ss' ;
    sdt = string(dt) ; 
    SampleNumber = getSampleNumber(conn, sdate, 'PRO') ;

    idold = checkFK(conn, "SELECT id FROM sample WHERE typesample='%s' and samplematrix_id=%s " + ...
    "and loadingdate='%s' and time='%s';", [typesample, idSampleMatrix, sdate, stime ] ) ; 
    if idold > 0 
    %   ss = sprintf( "The combination (Product, Quality, SamplePoint, Date, Time):(%s,%s,%s, %s, %s) is duplicated ", ...
    %       [ Product, Quality, SamplePoint, sdate, stime ]) ;  
    %   msgerror{1} = ss ;
       return ; 
    end    

    [idspec, ~ ] = getSpecId(conn, idproduct, idquality, '') ;  
    if idspec == 0 
       ss = sprintf( "There is no specification for (Product,Quality)" + ...
           ":(%s,%s) ", Product, Quality ) ;  
       msgerror{1} = ss ;
       return ; 
    end    

    sql = "SELECT v.shortname variable, d.variable_id, null min, null max " + ...
        " FROM dsamplematrix d, variable v  " + ...
        " WHERE d.variable_id=v.id and d.samplematrix_id =%s " + ...
        " and not exists(SELECT * FROM dspec d2, samplematrix sm, spec sp" + ...
        " WHERE sm.product_id=sp.product_id and sm.quality_id=sp.quality_id and sp.typeSpec='GEN'" + ...
        " and d.variable_id = d2.variable_id)  " + ...
        "UNION " + ...
        "SELECT v.shortname variable, d.variable_id, min, max " + ...
        " FROM dsamplematrix d, variable v, dspec d2, samplematrix sm, spec sp " + ...
        " WHERE d.variable_id=v.id and d.samplematrix_id =%s and sp.typeSpec='GEN' " + ...
        " and d.samplematrix_id=sm.id and d2.spec_id=sp.id " + ...
        " and sm.product_id=sp.product_id and sm.quality_id=sp.quality_id " + ...
        " and d.variable_id = d2.variable_id; ";
    sql = sprintf(sql, idSampleMatrix, idSampleMatrix) ; 
    limits = select(conn, sql ); 
    if height(limits) == 0
       ss = sprintf( "The variables for (Product, Quality, SamplePoint, Date, Time):(%s,%s,%s, %s, %s) are not table Spec.", ...
           [ Product, Quality, SamplePoint, sdate, stime ]) ;  
       msgerror{1} = ss ;
       return ; 
    end     
    sql = "INSERT INTO Sample(typesample, spec_id, customer, samplematrix_id, " + ...
        " product_id, quality_id, createdby_id, creationdate, "+ ...  
      " loadingdate, time,  Description, SampleNumber, SamplePoint_id, article_no) " + ...
      "VALUES( '%s', %s, '%s', %s, %s, %s, %s, '%s', '%s', '%s', '%s', '%s', %s, 0) " ; 
        
    values = [typesample, idspec, Owner,  idSampleMatrix,  idproduct, idquality, iduser, sdt, sdate,  stime, Description, SampleNumber, idSamplePoint ] ; 

    sql = sprintf(sql, values); 
    execute(conn, sql) ;  
    T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
    idsample = double( T.x(1) ); 

    insertmeasurement(conn, idsample, limits) ; 
    commit(conn) ;     
    %disp("Paso insert;") ; 

end % function



function  inidate = getFirstday(conn, date0, Frequency)

inidate = date0 ; 
 switch Frequency
   case '1/2 year'
     q = floor((month(date0)-1)/6)+1 ;
     switch  q      
        case 1
          date1 = datetime(year(date0),1,1) ;
        case 2
          date1 = datetime(year(date0),7,1) ; 
     end
     inidate = firstNonHolidays(conn, date1 ) ; 
   case 'Month'               
     date1 = datetime(year(date0),month(date0),1) ;
     inidate = firstNonHolidays(conn, date1 ) ; 

   case 'Quarter'             
     q = floor((month(date0)-1)/3)+1 ;
     switch  q      
        case 1
          date1 = datetime(year(date0),1,1) ;
        case 2
          date1 = datetime(year(date0),4,1) ;
        case 3
          date1 = datetime(year(date0),7,1) ; 
        case 4    
          date1 = datetime(year(date0),10,1) ; 
      end
      inidate = firstNonHolidays(conn, date1 ) ; 

    case 'Week'        
      date1 = date0 - hours( (weekday( date0 )-2) * 24 ) ; 
      inidate = firstNonHolidays(conn, date1 ) ; 
  end         
end
 
function inidate2 = firstNonHolidays(conn, inidate)

offset = 0 ; 
sql = "SELECT * FROM Holidays where date='%s'; " ;
inidate.Format = "yyyy-MM-dd" ; 
sql = sprintf(sql, inidate) ; 
T = select(conn, sql) ; 
while not( isempty(T) ) 
   date1 = datetime( inidate + hours(24) ) ; 
   date1.Format='yyyy-MM-dd'; 
   sql = "SELECT * FROM Holidays where date='%s'; " ;
   sql = sprintf(sql, date1) ; 
   T = select(conn, sql) ; 
   offset = offset + 1 ; 
end    

date1 = inidate + hours(24*offset)  ; 
date1.Format='yyyy-MM-dd'; 
inidate2 = string(date1) ;  

end