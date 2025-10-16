% This function loads data from logisticdata to the table sample and measuremnts adding in measurement table the limits for each  measurement (variable)
% according to specfications of the product and client 
function  [msgerror, pendingdata] = loadCustomerSample(conn, sdate, iduser)

% First we eliminate sample rows whose ordernumber_PVS and loadingdate are
% not in logisticdata table
execute(conn, "DELETE FROM sample WHERE typesample='CLI' and not exists(SELECT * " + ...
    " FROM logisticdata l WHERE sample.loadingdate=substring(CONVERT(VARCHAR,l.date,20),1,10)" + ...
    " and sample.ordernumber_PVS=l.ordernumber_PVS)") ; 

sdate = string(sdate) ;
msgerror = {'*********Error Messages from Customer Loadings******'} ; 

sql = "SELECT date, time, name_client, ordernumber_PVS, article_no, " + ...
    "ordernumber_client, description, loading_ton FROM logisticdata WHERE date is null" ; 
pendingdata = select(conn, sql) ; 

sql = "SELECT 'U' typerow, s.id id, " + ...
 " l.date loadingdate, l.time, l.name_client, l.ordernumber_PVS, " + ...
 " l.article_no, l.ordernumber_client, l.Description, l.loading_ton, s.testdate," + ...
 " p.name product, q.name quality, s.customer, s.product_id, s.quality_id, s.articlecode, " + ...
 " s.createdby_id, substring( CONVERT(VARCHAR,l.date,20),1,10) date2, sp.COA, sp.certificaat, " + ...
 " sp.COC, sp.Day_COA, sp.opm, sp.onedecimal " + ... 
" FROM sample s, product p, quality q,  logisticdata l, spec sp  " + ...
" WHERE s.spec_id=sp.id and s.loadingdate='%s' and s.product_id=p.id and " + ...
" s.quality_id=q.id and s.typesample='CLI' and s.ordernumber_PVS = l.ordernumber_PVS" + ...
" and s.loadingdate=substring( CONVERT(VARCHAR,l.date,20),1,10) " + ...
"UNION " + ...
"SELECT 'E1' typerow, 0 id, l.date loadingdate, l.time, l.name_client, l.ordernumber_PVS, " + ...
" l.article_no, l.ordernumber_client, l.Description, l.loading_ton, '' testdate, " + ...
"' ' product, ' ' quality, ' ' customer, " + ...
" 0 product_id, 0 quality_id, 0 articlecode, 0 createdby_id, ' ' date2,  " + ...
"' ' COA, ' ' certificaat, ' ' COC, ' ' Day_COA, ' ' opm, ' ' onedecimal  " + ...            
"FROM logisticdata l WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) ='%s' " + ...
"and not exists(select * from map m WHERE l.article_no = m.articlecode) " + ...
" UNION " + ...
" SELECT 'E2' typerow, 0 id, l.date loadingdate, l.time, l.name_client, l.ordernumber_PVS, " + ...
" l.article_no, l.ordernumber_client, l.Description, l.loading_ton, '' testdate, " + ...
" p.name product, q.name quality, ' ' customer, " + ...
" m.product_id, m.quality_id, m.articlecode, 0 createdby_id, ' ' date2,  " + ...
" ' ' COA, ' ' certificaat, ' ' COC, ' ' Day_COA, ' ' opm, ' ' onedecimal  " + ...    
"FROM logisticdata l, map m, product p, quality q " + ...
"WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) ='%s' " + ...
" and m.product_id=p.id and m.quality_id=q.id " + ...
" and l.article_no = m.articlecode and not exists(SELECT * FROM spec s WHERE  " + ...
" s.product_id=m.product_id and s.quality_id=m.quality_id and s.customer=l.name_client) " + ...
" UNION " + ...
" SELECT 'N' typerow, 0 id, l.date loadingdate, l.time, l.name_client, l.ordernumber_PVS, " + ...
" l.article_no, l.ordernumber_client, l.Description, l.loading_ton, '' testdate, p.name product, " + ...
" q.name quality, s.customer,  m.product_id, m.quality_id, m.articlecode, " + ...
" %s createdby_id, substring( CONVERT(VARCHAR,l.date,20),1,10) date2,  " + ...
" s.COA, s.certificaat, s.COC, s.Day_COA, s.opm, s.onedecimal " + ...    
" FROM logisticdata l, map m, product p, quality q, spec s " + ...
" WHERE SUBSTRING(CONVERT(VARCHAR,l.date,20),1,10) = '%s'  " + ...
" and l.article_no = m.articlecode and " + ...
" s.product_id=m.product_id and s.quality_id=m.quality_id and s.customer=l.name_client " + ... 
" and m.product_id=p.id and m.quality_id=q.id and " + ...
" not exists( SELECT * FROM sample s WHERE s.ordernumber_PVS = l.ordernumber_PVS" + ...
" and s.loadingdate=substring( CONVERT(VARCHAR,l.date,20),1,10) )" ; 

sql = sprintf( sql, [sdate, sdate, sdate, iduser, sdate] ) ; 
nerror = 0 ; 
data = select( conn, sql ) ; 
for i=1:height(data)
    row = {data.loadingdate(i), data.time(i), data.name_client(i), ...
        data.ordernumber_PVS(i), data.article_no(i), ...
        data.ordernumber_client(i), data.Description(i), data.loading_ton(i) } ; 

    if strcmp(data.typerow(i), 'E1')
       nerror = nerror + 1; 
       msgerror{length(msgerror)+1}= sprintf( "Row %s. It is impossible to " + ...
           " find ArticleCode %s in table Map  "...
           , string(nerror), string( data.article_no(i)) )  ;  
       pendingdata = [pendingdata;row];
       continue ; 
    end 
    Product = strtrim( data.product(i) ) ; 
    Quality = strtrim( data.quality(i) ) ; 
    idproduct = string(data.product_id(i) ); 
    idquality = string(data.quality_id(i) ); 
    COA = strtrim(string(data.COA(i) )); 
    certificaat = strtrim(string(data.certificaat(i) ));
    COC = strtrim(string(data.COC(i) ));
    Day_COA = strtrim(string(data.Day_COA(i) ));
    opm = strtrim(string(data.opm(i) ));
    onedecimal = strtrim(string(data.onedecimal(i) ));

    if strcmp(data.typerow(i), 'E2')
       nerror = nerror + 1;  
       name_client = strtrim( string(data.name_client(i)) ) ; 
       product = strtrim( string(data.product(i)) ) ; 
       quality = strtrim( string(data.quality(i)) ) ; 
       articlecode = data.articlecode(i) ; 
       msgerror{length(msgerror)+1}= sprintf( "Row %s, It is impossible to find " + ...
           "the combination (Customer, Product, Quality): (%s , %s , %s) in table CustomerList " + ...
           " when articlecode = %d ",  ...
           string(nerror), name_client, product, quality, articlecode );  
          pendingdata = [pendingdata;row];
       continue ;         
    end 
    customer = string( strtrim( data.customer(i) )) ; 

    [idspec, ~ ] = getSpecId(conn, idproduct, idquality, customer) ; 
    sql = "SELECT v.shortname variable, variable_id, min, max FROM dspec d, variable v WHERE d.variable_id=v.id and d.spec_id=%s; ";
    sql = sprintf(sql, string(idspec)) ; 
    % "; idspec=" + string(idspec) +
    %insertlog(conn, "Pass1", "sql="  + ...
    %     "; idquality="+string(idquality) + ...
    %    "idproduct="+string(idproduct) + ";customer="+string(customer) ) ; 
    
    if length(idspec) == 1  && idspec > 0
        limits = select(conn, sql ); 
        samplenumber = getSampleNumber(conn, sdate, 'CLI') ; 
        if strcmp( data.typerow(i), 'N' )
            % Insertion of new samples into the database
            msgerror2 = insertsample(conn, data, i, idspec, iduser, samplenumber, limits ) ; 
            msgerror = [msgerror, msgerror2 ] ; 
        end
        if strcmp( data.typerow(i), 'U' )
            % Insertion of new samples into the database
            ddate = strtrim(string(data.loadingdate(i) ));  
            sql1 = "UPDATE sample set samplenumber='%s', COA='%s', " + ...
                " certificaat='%s', COC='%s', Day_COA='%s', opm='%s', onedecimal='%s' " + ...
                " WHERE loadingdate='%s' and  ordernumber_PVS=%s" ; 
            sql = sprintf(sql1, [samplenumber, COA, certificaat, COC, Day_COA, ...
                opm, onedecimal, ddate{1} ,data.ordernumber_PVS(i) ]) ; 
            execute(conn, sql) ;
        end
        
        % Update with the last info from logisticdata table
        if strcmp( data.typerow(i), 'U' ) 
            % Updating for existing samples
           updatesample(conn, data, i, limits) ; 
        end            
    elseif length(idspec) > 1
      nerror = nerror + 1 ;   
      ss = "Row %s. The specification for the combination of: (Product, Quality, Customer)=(%s,%s,%s) is duplicated." ; 
      ss = sprintf(ss, [string(nerror), Product, Quality, customer]) ; 
      msgerror{length(msgerror)+1}= ss ;           
    elseif idspec == 0 
      nerror = nerror + 1 ;   
      ss = "Row %s. It is impossible to find a specification for the combination of: (Product, Quality, Customer)=(%s,%s,%s)" + ...
          " in table CustomerList ." ; 
      ss = sprintf(ss, [string(nerror), Product, Quality, customer]) ; 
      msgerror{length(msgerror)+1}= ss ;         
    end   
end    
if length(msgerror) == 1
   msgerror = {} ; 
end
end % function




function updatesample(conn, data, i,  limits) 

    idsample =  data.id(i)  ; 
    %Remark = strtrim( string( data.remark(i)) ); 
    %BatchNumber = strtrim( string( data.batchnumber(i) ) ); 
    %ContainerNumber = string(data.containernumber(i) ) ; 
    %sql = "UPDATE sample set  Remark='%s', BatchNumber='%s', ContainerNumber='%s' WHERE id=%s" ;    
    %values = [ Remark, BatchNumber, ContainerNumber, idsample ] ; 
    %sql = sprintf( sql, values ) ;      
    %execute(conn, sql)
    for j=1:height(limits) 
       variable = limits.variable(j) ; 
       variable_id = limits.variable_id(j) ; 
       min = limits.min(j) ;
       if ismissing(min) || str2double(min) < 0
           min = "NULL" ; 
       %else
       %    min = mat2str(min) ; 
       end    
       max = limits.max(j) ; 
       if ismissing(max) || str2double(max) < 0 
           max = "NULL" ; 
       %else     
       %    max = mat2str(max) ;            
       end    
       sql = "SELECT sample_id FROM measurement WHERE sample_id =%d and variable_id=%d " ; 
       sql = sprintf(sql,  idsample, variable_id) ; 
       T = select(conn, sql) ; 
       if height(T) == 0
          sql2 = "INSERT INTO measurement(sample_id, variable_id, variable, min, max, value ) " + ...
              "VALUES (%s, %s, '%s', '%s', '%s', -1)" ; 
          values = [ string(idsample), string(variable_id), variable, min, max ] ;  
          sql2 = sprintf( sql2, values ) ; 
          execute(conn, sql2) ;
       else
          if not( strcmp(min, "null") ) && not( strcmp(max, "null") )
             sql2 = "UPDATE Measurement SET min='%s', max='%s' WHERE sample_id=%d AND variable_id=%d; " ; 
             sql2 = sprintf(sql2, strtrim(min{1}), strtrim(max{1}), idsample, variable_id) ; 
          end 
          if not( strcmp(min, "null") ) &&  strcmp(max, "null")
             sql2 = "UPDATE Measurement SET min='%s' WHERE sample_id=%d AND variable_id=%d;" ; 
             sql2 = sprintf(sql2, strtrim(min{1}),  idsample, variable_id) ; 
          end 
          if  strcmp(min, "null")  && not( strcmp(max, "null") )
             sql2 = "UPDATE Measurement SET  max='%s' WHERE sample_id=%d AND variable_id=%d;"  ; 
             sql2 = sprintf(sql2, strtrim(max{1}),  idsample, variable_id) ; 
          end 
          execute(conn, sql2) ;            
       end
    end
    commit(conn) ; 
end


function msgerror = insertsample(conn, data, i, idspec, iduser, samplenumber, limits )

    msgerror = {} ; 
    idproduct = data.product_id(i) ; 
    idquality = data.quality_id(i) ; 
    articlecode = data.articlecode(i) ; 
    customer = data.customer(i) ; 
    Description = strtrim( data.Description(i) ) ; 
    loadingdate = strtrim( data.date2(i) ) ; 
    stime = strtrim( data.time(i) ) ; 
    dt = datetime ; 
    dt.Format = 'yyyy-MM-dd HH:mm:ss' ;
    sdt = string(dt) ; 
    loading_ton = data.loading_ton(i) ;
    ordernumberPVS = strtrim( string(data.ordernumber_PVS(i)) ); 
    article_no = strtrim(string(data.article_no(i)) );      
    ordernumber_client = strtrim( string( data.ordernumber_client(i) )); 
    Remark = ""; 
    BatchNumber = ""; 
    ContainerNumber = "" ; 
    certificaat = string(data.certificaat(i) ) ; 
    COA = string(data.COA(i) ) ; 
    COC = string(data.COC(i) ) ; 
    Day_COA = string(data.Day_COA(i) ) ; 
    opm = string(data.opm(i) ) ; 
    onedecimal = string(data.onedecimal(i) ) ; 

  %  product = strtrim( data.product(i) ); 
  %  quality = strtrim( data.quality(i) ); 
    %[SamplePoint, idSampleMatrix] = getSamplePoint(conn, idproduct, idquality) ; 

  %  if idSampleMatrix == 0
  %      ss = sprintf("There is no SamplePoint for Product=%s and Quality=%s", string(product), string(quality) ) ; 
  %      msgerror{length(msgerror)+1}= ss;  
  %  else   

      sql = "INSERT INTO Sample(typesample, spec_id, product_id, quality_id, articlecode, customer, " + ...
          "createdby_id, creationdate, loadingdate, time, ordernumber_PVS, article_no, ordernumber_client, " + ...
          "Description, loading_ton, samplenumber,  Remark, BatchNumber, ContainerNumber, " + ...
          "certificaat, COA, COC, Day_COA, opm, onedecimal) " + ...
          " VALUES( 'CLI', %s, %s, %s, %s, '%s', %s, '%s', '%s', '%s', '%s', '%s', " + ...
          "'%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s', '%s');" ; 

       values = [ idspec, idproduct, idquality, articlecode, customer, ...
           iduser, sdt,  loadingdate, stime, ordernumberPVS, article_no, ordernumber_client, ...
           Description, loading_ton, samplenumber,  Remark, BatchNumber, ...
           ContainerNumber, certificaat, COA, COC, Day_COA, opm, onedecimal] ; 
       sql = sprintf( sql, values ) ;     

       execute(conn, sql) ;  
       T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
       idsample = T.x(1) ; 
       if strcmp(COA, "X") || strcmp(Day_COA, "X")
          insertmeasurement(conn, idsample, limits) ; 
       end
       commit(conn) ; 
  %  end 

end % function


%function [SamplePoint, idSampleMatrix] = getSamplePoint(conn, idproduct, idquality) %
%SamplePoint = "" ; 
%idSampleMatrix = 0 ; 
%sql = "SELECT samplepoint, min(id) id, count(*) cnt FROM samplematrix " + ...
%    " WHERE product_id=%d  and quality_id=%d "+...
%    " GROUP BY samplepoint;" ; 

%sql = sprintf( sql, [idproduct, idquality]) ; 
%T = select(conn, sql ) ; 
%if height(T)>0 && T.cnt(1) == 1 
%   SamplePoint = T.samplepoint(1) ;  
%   idSampleMatrix = T.id(1) ; 
%end 

%end % sample point 
