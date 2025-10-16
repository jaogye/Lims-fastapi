function [newdata, msgerror, stat, pendingdata] = saveClientSpec(conn, data)
% This function checks the validity and updates client data against the database 
% and displays corresponding msgs of errors. The output table is obtained  

nerror = 1 ; 
pendingdata = table() ; 
newdata = table() ; 

ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'CustomerList') ; 

if not(isempty(msgerror))
   newdata = getSpec(conn, 'CLI') ; 
   return ; 
end

[indexCols, tests, msgerror] = getDataVariables(conn, data, msgerror) ; 
if not(isempty(msgerror))
   newdata = getSpec(conn, 'GEN') ; 
   return ; 
end

data.Certificaat = upper(data.Certificaat) ; 
data.COA = upper(data.COA) ; 
data.COC = upper(data.COC) ; 
data.Day_COA = upper(data.Day_COA) ; 

for i = 1:height(data) 
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    Customer =  strtrim( data.Customer(i)) ; 
    Action = strtrim( data.Action(i) );    
    COC = strtrim( string(data.COC(i) )) ; 
    COA = strtrim( string(data.COA(i) )) ; 

    if strcmp( data.Action(i), "D" ) 
       if not( ismissing( str2double( data.id(i) ) ))
          sql = "DELETE FROM spec WHERE id =%s ;"  ; 
          sql = sprintf( sql ,data.id(i) ) ; 
          execute(conn,sql) ; 
          commit(conn) ; 
          ndeleted = ndeleted  + 1 ; 
       else
          msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s. In row %s The id=%s is not valid. " + ...
              "The row is not deleted." , Action, nerror, data.id(i)  ) ; 
         if strcmp(data.Action(i), Action)
            nerror=nerror+1 ;   
            data.Action(i) = "*" + Action ; 
         end             
       end
    end % if 

    if strcmp( data.Action(i), "U" )                                                        
      [idproduct, idquality, ~, limits,  msgerror2 ] = validateClientSpec(conn, data, i, tests, indexCols, nerror )  ;
      nerror = nerror + length(msgerror2) ;       
      if isempty(msgerror2)
         nIntervals = countSpec( limits) ; 
         if nIntervals == 0 && not( checkNotNull( COC ) &&  strcmp( COC, "X")) && checkNotNull( COA )  && not(strcmp( COA, "N" ))
             msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "The combination (Customer, Product, Quality):(%s,%s,%s) has no intervals. The row is not updated.", ...
               [Action, nerror, Customer, Product, Quality] ) ; 
             data.Action(i) = "*" + Action ; 
             nerror = nerror + 1 ; 
         end
         id = checkFK( conn, "SELECT id FROM spec WHERE id=%s", data.id(i) ) ; 
         if id > 0
            cols = [ "typespec", "customer", "product_id", "quality_id", "Status", "Certificaat","Opm","COA","Day_COA", "COC","Visual", "OneDecimal" ] ; 
            values = {"CLI", Customer, idproduct, idquality, data.Status(i), data.Certificaat(i), data.Opm(i), data.COA(i), data.Day_COA(i), data.COC(i), data.Visual(i), data.OneDecimal(i) } ; 
            sql = getupdatespec(string(id), cols, values, limits, tests)  ;
            execute(conn,sql) ; 
            updatedSpec(conn, string(id), limits, tests) ; 
            commit(conn) ; 
            nupdated = nupdated + 1 ;           
          else
            msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "Invalid id=%s. Upload this file with the lastest version. The row is not updated.", ...
               [Action, nerror,data.id(i)] ) ; 
            data.Action(i) = "*" + Action ; 
            nerror = nerror + 1 ;              
         end    
       else                
         msgerror = [msgerror, msgerror2 ] ;                      
         data.Action(i) = "*" + Action ;           
      end
    end

    if strcmp( data.Action(i), "I" ) 
       [idproduct, idquality, idspec, limits,  msgerror2 ]  = validateClientSpec(conn, data, i, tests, indexCols, nerror);
       nerror = nerror + length(msgerror2) ; 
       if isempty(msgerror2) 
          nIntervals = countSpec( limits) ;  
          if nIntervals == 0 && not( checkNotNull( COC ) &&  strcmp( COC, "X")) && checkNotNull( COA )  && not(strcmp( COA, "N" )) 
             msgerror{ length(msgerror)+1 } = sprintf("Action %s, row %s. " + ...
             "COA='X' and the combination (Customer, Product, Quality):(%s,%s,%s) has no intervals. The row is not inserted.", ...
             [Action, nerror, Customer, Product, Quality] ) ; 
             return 
          end                
       end
       if idspec > 0 
          msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
            "The combination (Customer, Product, Quality):(%s,%s,%s) already exists. The row is not inserted.", ...
            [ Action, nerror, Customer, Product, Quality] ) ; 
          data.Action(i) = "*" + Action ;
          nerror = nerror + 1 ; 
       end       
       if isempty(msgerror2)
          cols = [ "typespec", "customer", "product_id", "quality_id", "Status", "Certificaat","Opm","COA","Day_COA", "COC","Visual", "OneDecimal" ] ; 
          values = {"CLI", Customer, idproduct, idquality, data.Status(i), data.Certificaat(i), data.Opm(i), data.COA(i), data.Day_COA(i), data.COC(i), data.Visual(i), data.OneDecimal(i) } ; 
          sql = getinsertspec(cols, values ,limits, tests) ;
          execute(conn,sql) ; 
          ninserted = ninserted + 1 ; 
          T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
          idspec = T.x(1) ; 
          updatedSpec(conn, idspec, limits, tests) ; 
          commit(conn) ; 
        else 
          msgerror = [msgerror, msgerror2 ] ;                      
          data.Action(i) = "*" + Action ; 
       end
    end     
end

for i=1:length(msgerror)
   msgerror{1,i} = mat2str(i) + ")" + msgerror{1,i} ; 
end

stat = table(ndeleted, nupdated, ninserted) ; 
newdata = getSpec(conn, 'CLI') ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end % function saveclienttable


% -------------------------------------------------------

function [idproduct, idquality, idspec, limits,  msgerror ]  = validateClientSpec(conn, data, i, tests, indexCols, nerror)

    msgerror = {} ;
    limits = {}  ;
    idproduct = 0 ;
    idquality = 0 ;
    idspec=0;    
    i = int64(i) ; 
    Action = strtrim(data.Action(i)) ;
    Customer =  strtrim( data.Customer(i)) ; 
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    Certificaat = strtrim( data.Certificaat(i) ) ; 
    Day_COA = strtrim( string(data.Day_COA(i)) ) ; 
    COA = strtrim( string(data.COA(i)) ) ; 
    COC = strtrim( string(data.COC(i) )) ; 
    OneDecimal = strtrim( string(data.OneDecimal(i) )) ; 

    ok = checkNotNull( Customer ) ; 
    if not(ok)      
       nerror=nerror+1 ;  
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. Customer must not be null." , ...
           [Action,  nerror] ) ;  
       return ; 
    end

    ok = checkNotNull( Product ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. Product must not be null.", ...
           [Action,  nerror] ) ; 
       return ; 
    end
    
    ok = checkNotNull( Quality ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. Quality must not be null.", ...
           [Action, nerror] ) ;
       return ; 
    end
    
    idproduct = checkFK( conn, "SELECT id FROM product WHERE name='%s';",  Product  ) ; 
    if idproduct == 0 
       msgerror{ length(msgerror)+1 } = sprintf(  ...
           "Action=%s, row %s.  Product %s is not found in table Product." , ...
           [Action, nerror, Product] ) ;
       return ;        
    end

    idquality = checkFK( conn, "SELECT id from quality where name='%s' ;",  Quality  ) ; 
    if idquality == 0 
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, row %s. " + ...
           "The quality %s is not found in table quality.", ...
           [Action,nerror, Quality] ) ;      
       return ; 
    end

    if strcmp(Action, "U") && ismissing( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), nerror] ) ;
       return ;
    end

    idspecgen = checkFK( conn, "SELECT id FROM spec WHERE typespec='GEN' AND product_id=%d and quality_id=%d;",  [idproduct, idquality] ) ; 
    if idspecgen == 0 
      msgerror{ length(msgerror)+1 } = sprintf( "Action %s, row %s. The combination " + ...
           "(Product, Quality)=(%s,%s) must have a product specification in " + ...
           "table Spec." , [Action, nerror, Product, Quality  ] ) ;       
       return ; 
    end

    ok = checkValueList(  Certificaat, "Y,N,M,Q" ); 
    if not(ok)     
       msgerror{ length(msgerror)+1 } = sprintf( ...
           "Action=%s, row %s. The Certificaat %s must contain one of these values %s " , ...
           [Action, nerror, Certificaat, "Y,N,M,Q" ]) ;
       return ; 
    end

    if checkNotNull( Day_COA )  && not( strcmp(  Day_COA, "X" )  || strcmp(Day_COA,"N" ) )   
       msgerror{ length(msgerror)+1 } = sprintf( ...
           "Action=%s, row %s. The Day_COA must be X or null " , ...
           [Action, nerror ]) ;
       return ; 
    end
      
    if checkNotNull( COA ) && not( strcmp( COA,"X" ) || strcmp(COA,"N" ) )   
       msgerror{ length(msgerror)+1 } = sprintf( ...
           "Action=%s, row %s. The COA must be X, N or null " , ...
           [Action, nerror ]) ;
       return ; 
    end

    if checkNotNull( OneDecimal ) && not( strcmp( OneDecimal,"Y" )  )   
       msgerror{ length(msgerror)+1 } = sprintf( ...
           "Action=%s, row %s. The OneDecimal must be Y or blank " , ...
           [Action, nerror ]) ;
       return ; 
    end


    if checkNotNull( COC ) && not( strcmp( COC, "X" )  || strcmp(COC,"N" ) )
       msgerror{ length(msgerror)+1 } = sprintf( ...
           "Action=%s, row %s. The COC must be X or null " , ...
           [Action, nerror ]) ;
       return ; 
    end
    
   idspec = checkFK( conn, "SELECT id FROM spec WHERE typespec='CLI' AND product_id=%s " + ...
       "AND quality_id=%s AND Customer='%s';",  [idproduct, idquality, Customer]  ) ; 

   [limits, msgerror] = getLimits(conn, 'CLI', data, tests, indexCols, msgerror, i) ; 

    if strcmp( strtrim(data.conc(i)), "") && strcmp( data.Day_COA(i), "X" ) 
       msgerror{ length(msgerror)+1 } = sprintf("Action %s, row %s. " + ...
           "Day_COA='X' and the combination (Customer, Product, Quality)" + ...
           ":(%s,%s,%s) has no conc interval. The row is not inserted.", ...
          [Action, nerror, Customer, Product, Quality] ) ; 
       return 
    end         
    
end % ValidateClientSpec


% ----------------------------------------------------------------------------------------
% ----------------------------------------------------------------------------------------




%function id = insertclient(conn, name) 
%sql = "insert into client(name) values('"+ name + "');" ; 
%execute(conn,sql) ;
%commit(conn) ; 
%T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
%id = T.x(1) ; 
%end % insertclient 




