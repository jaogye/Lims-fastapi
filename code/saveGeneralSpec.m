function [newdata, msgerror, stat, pendingdata] = saveGeneralSpec(conn, data)
% This function checks the validity and updates general specifications against the database and displays corresponding msgs of errors. The output table is obtained  

nerror = 1 ; 

pendingdata = table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Spec') ; 

if not(isempty(msgerror))
   newdata = getSpec(conn, 'GEN') ; 
   return ; 
end

[indexCols, tests, msgerror] = getDataVariables(conn, data, msgerror) ; 
if not(isempty(msgerror))
   newdata = getSpec(conn, 'GEN') ; 
   return ; 
end

% Formatted string output
mmsg.notokproduct = "Action=%s, row %s, id:%s. The product %s is not found in table product."  ;
mmsg.notokquality = "Action=%s, row %s, id:%s. The quality %s is not found in table quality."  ;
mmsg.row = "Action=%s, row %s, id:%s. %s"  ; 
mmsg.ColumnValue = "Action=%s, row %s, id:%s. column:%s value:%s. %s"  ; 
mmsg.Column = "Action=%s, row %s, id:%s. column:%s. %s"  ; 

mmsg.queryproduct = "SELECT id from product where name='%s' ;" ;
mmsg.queryquality = "SELECT id from quality where name='%s' ;" ;
mmsg.querygeneralspec = "SELECT id from spec where typespec='GEN' and product_id=%d qnd quality_id =%d; " ;

for i = 1:height(data) 
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    Action = strtrim( data.Action(i) );

    if strcmp( Action, "D" ) 
       if not( ismissing( str2double( data.id(i) ) ))
          msgerror2 = checkChildren(conn, 'Spec' , data.id(i)  ) ; 
          if isempty(msgerror2)
             sql = "DELETE FROM spec WHERE id =" + data.id(i) + ";"  ; 
             execute(conn,sql) ; 
             commit(conn) ; 
             ndeleted = ndeleted  + 1 ; 
          else  
              msgerror = [ msgerror msgerror2 ] ; 
              data.Action(i) = "*" + Action ; 
          end
        else
          msgerror{ length(msgerror)+1 } =  sprintf( mmsg.row, [Action, nerror, data.id(i), "Row not found, row not deleted. "  ] ) ; 
          data.Action(i) = "*" + Action ; 
       end
    end % if 

    if strcmp( data.Action(i), "U" ) 
      [idproduct, idquality, idVariable1, idVariable2, idVariable3, ~, limits,  msgerror2 ] = validateGeneralSpec(i, conn, data, tests, indexCols, mmsg, nerror )  ;
      if idVariable1 == 0
         idVariable1 = NaN ;
      end
      if idVariable2 == 0
         idVariable2 = NaN ;
      end
      if idVariable3 == 0
         idVariable3 = NaN ;
      end
      
      nerror = nerror + length(msgerror2) ;      
      if isempty(msgerror2)
         nIntervals = countSpec( limits) ;  
         if nIntervals == 0  
            msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "The combination (Product, Quality):(%s,%s) has no interval. The row is not updated.", ...
               [Action, nerror, Product, Quality] ) ; 
            data.Action(i) = "*" + Action ; 
            nerror = nerror + 1 ; 
         end  
      end 
      if isempty(msgerror2)
          id = checkFK( conn, "SELECT id FROM spec WHERE id=%s", data.id(i) ) ; 
          if id > 0
            cols = [ "typespec",  "product_id", "quality_id", "TDS", "Visual", "Variable1_id", "Variable2_id", "Variable3_id" ] ; 
            values = {"GEN",  idproduct,  idquality, data.TDS(i), data.Visual(i), idVariable1, idVariable2, idVariable3  } ; 
            sql = getupdatespec(data.id(i), cols, values ,limits, tests)  ;
            execute(conn,sql) ; 
            updatedSpec(conn, data.id(i), limits, tests) ; 
            commit(conn) ;
            nupdated = nupdated + 1 ; 
          else
            msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "Invalid id=%s. Upload this file with the lastest version. The row is not updated.", ...
               [Action, nerror, data.id(i)] ) ; 
            data.Action(i) = "*" + Action ; 
            nerror = nerror + 1 ; 
          end
        else 
         msgerror = [msgerror, msgerror2 ] ; 
         data.Action(i) = "*" + Action ; 
       end
    end

    if strcmp( data.Action(i), "I" ) 
       [idproduct, idquality, idVariable1, idVariable2, idVariable3, idspec, limits,  msgerror2 ] = validateGeneralSpec(i, conn, data, tests, indexCols, mmsg, nerror );          
       if idVariable1 == 0
          idVariable1 = NaN ;
       end
       if idVariable2 == 0
          idVariable2 = NaN ;
       end
       if idVariable3 == 0
          idVariable3 = NaN ;
       end
       
       nerror = nerror + length(msgerror2) ;  
       if idspec > 0 
          msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "The combination (Product, Quality):(%s,%s) already exist. The row is not inserted.", ...
               [Action, nerror, Product, Quality] ) ; 
          data.Action(i) = "*" + Action ; 
          nerror = nerror + 1 ; 
       end    
       if isempty(msgerror2)
          nIntervals = countSpec( limits) ; 
          if nIntervals == 0 
             msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "The combination (Product, Quality):(%s,%s) has no interval. The row is not inserted.", ...
               [Action, nerror, Product, Quality] ) ; 
             data.Action(i) = "*" + Action ; 
             nerror = nerror + 1 ; 
          end 
       end
       if isempty(msgerror2)
          cols = [ "typespec",  "product_id", "quality_id", "TDS", "Visual", "Variable1_id", "Variable2_id", "Variable3_id"  ] ; 
          values = {"GEN",  idproduct, idquality, data.TDS(i), data.Visual(i), idVariable1, idVariable2, idVariable3 } ; 
          sql = getinsertspec(cols, values, limits, tests) ;
          execute(conn,sql) ; 
          T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
          idspec = T.x(1) ; 
          ninserted = ninserted + 1 ; 
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
newdata = getSpec(conn, 'GEN') ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end % function savegeneraltable


% -------------------------------------------------------


function [idproduct, idquality, idVariable1, idVariable2, idVariable3, idspec, limits,  msgerror ] = validateGeneralSpec(i, conn, data, tests, indexCols, mmsg, nerror )

    msgerror = {} ;
    limits = {}  ;
    idproduct = 0 ;
    idquality = 0 ;
    idVariable1 = 0 ;
    idVariable2 = 0 ;
    idVariable3 = 0 ;
    
    idspec=0 ; 
    i = int64(i) ; 
    Action = data.Action(i) ;
    
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    Variable1 =  strtrim( data.Variable1(i)) ; 
    Variable2 =  strtrim( data.Variable2(i)) ; 
    Variable3 =  strtrim( data.Variable3(i)) ; 
    
    ok = checkNotNull( Product ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, ...
           [Action,  nerror, data.id(i), "Product must be not null."] ) ;
       return ; 
    end

    ok = checkNotNull( Quality ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, ...
           [Action, nerror, data.id(i), "Quality must be not null."] ) ;
       return ; 
    end

    idproduct = checkFK( conn, mmsg.queryproduct, Product ) ; 
    if idproduct == 0 
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.notokproduct, ...
           [Action, nerror, data.id(i), Product ] ) ;
       return ; 
    end

    idquality = checkFK( conn, mmsg.queryquality, Quality ) ; 
    if idquality == 0
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.notokquality, ...
           [Action, nerror, data.id(i), Quality ] ) ;
       return ; 
    end

    if strcmp(Action, "U") && ismissing( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), nerror] ) ;
       return ;
    end
    
    idspec = checkFK( conn, "SELECT id FROM spec WHERE typespec='GEN' AND product_id=%d and quality_id=%d;",  [idproduct; idquality]  ) ;     
    [limits, msgerror] = getLimits(conn, 'GEN', data, tests, indexCols, msgerror, i) ; 
    % If Variable1 is null then omit
    if  checkNotNull( Variable1 ) 
       idVariable1 = checkFK( conn, "SELECT id From variable Where shortname='%s'", Variable1  ) ; 
       if idVariable1 == 0              
           msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Variable1:"+Variable1+" does not exist."   ] ) ;
           return ; 
       end
       interval1 = strtrim(data.(Variable1)(i) ) ; 
       if strcmp( interval1, '') 
           msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Interval in GenSpec of Variable1:"+Variable1+" does not exist."   ] ) ;
           return ; 
       end 
    end    

    if checkNotNull( Variable2 )  
       idVariable2 = checkFK( conn, "SELECT id From variable Where shortname='%s'", Variable2  ) ; 
       if idVariable2 == 0              
          msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Variable2:"+Variable2+" does not exist."   ] ) ;
          return ; 
       end
       interval2 = strtrim(data.(Variable2)(i) ) ; 
       if strcmp( interval2, '') 
          msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Interval in GenSpec of Variable1:"+Variable2+" does not exist."   ] ) ;
          return ; 
       end 
    end    

    if checkNotNull( Variable3 ) 
       idVariable3 = checkFK( conn, "SELECT id From variable Where shortname='%s'", Variable3  ) ; 
       if idVariable3 == 0              
          msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Variable3:"+Variable3+" does not exist."   ] ) ;
          return ; 
       end

       interval3 = strtrim(data.(Variable3)(i) ) ; 
       if strcmp( interval3, '') 
          msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Interval in GenSpec of Variable1:"+Variable3+" does not exist."   ] ) ;
         return ; 
       end 
    end    

end % ValidateGeneralSpec

