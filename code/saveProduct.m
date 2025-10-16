function [newdata, msgerror, stat, pendingdata] = saveProduct(conn, data)
% This function checks the validity and updates sample matrix (sample points)

nerror = 1 ; 
pendingdata = table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Product') ; 

if not(isempty(msgerror))
   newdata = getProduct(conn) ; 
   return ; 
end

% Formatted string output
mmsg.row = "Action=%s, row %s, id:%s. %s"  ; 
mmsg.ColumnValue = "Action=%s, row %s, id:%s. column:%s value:%s. %s"  ; 
mmsg.Column = "Action=%s, row %s, id:%s. column:%s. %s"  ; 

for i = 1:height(data) 
    Action = strtrim( data.Action(i)) ;     
    name =  strtrim( data.Name(i)) ;    
    bruto =  strtrim( data.Bruto(i)) ;    
    name_coa =  strtrim( data.Name_coa(i)) ;    
    ok = checkNotNull( bruto ) ; 
    if not(ok)      
       bruto = "" ; 
    end
        
    if strcmp( data.Action(i), "D" )        
        msgerror2 = checkChildren(conn, 'Product' , data.id(i)  ) ; 
        if isempty(msgerror2)        
           sql = "DELETE FROM Product WHERE id =%s;"  ; 
           sql = sprintf( sql ,data.id(i) ) ; 
           execute(conn,sql) ; 
           commit(conn) ; 
           ndeleted = ndeleted  + 1 ; 
        else
            msgerror = [ msgerror msgerror2 ] ; 
            data.Action(i) = "*" + Action ; 
        end  
    end % if 

    if strcmp( data.Action(i), "U" )        
       [~,   msgerror2 ] = validateProduct(i, conn, data, mmsg, nerror )  ;
       nerror = nerror + length(msgerror2) ;   
       if isempty(msgerror2)
          id = checkFK( conn, "SELECT id FROM Product WHERE id=%s", data.id(i) ) ; 
          if id > 0           
             sql = "UPDATE Product SET name='%s', bruto='%s', name_coa='%s' WHERE id=%s ;" ; 
             values = [name, bruto, name_coa, id ] ;  
             sql = sprintf(sql, values) ; 
             execute(conn,sql) ; 
             commit(conn) ; 
             nupdated = nupdated + 1 ;
          else
            msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "Invalid id. Upload this file with the lastest version. The row is not updated.", ...
               [Action, nerror] ) ; 
            data.Action(i) = "*" + Action ; 
            nerror = nerror + 1 ;                           
          end 
       else
           msgerror = [msgerror, msgerror2 ] ; 
           data.Action(i) = "*" + Action ; 
       end  
    end

    if strcmp( data.Action(i), "I" ) 
       [idproduct,   msgerror2 ] = validateProduct(i, conn, data, mmsg, nerror )  ;
       nerror = nerror + length(msgerror2) ;   
       if not( isempty(msgerror2) ) 
           msgerror = [msgerror, msgerror2 ] ; 
           data.Action(i) = "*" + Action ; 
       end
       if idproduct>0          
          msgerror{ length(msgerror)+1 } = sprintf("Action %s, row %s." + ...
              " Product:%s already exists", [Action,nerror, name ] ) ; 
           data.Action(i) = "*" + Action ; 
       end
       if idproduct==0 && isempty(msgerror2)
          sql = "INSERT into Product(name, bruto, name_coa) values ('%s', '%s', '%s' )" ; 
          sql = sprintf(sql, name, bruto, name_coa) ; 
          execute(conn,sql) ; 
          ninserted = ninserted + 1 ; 
          commit(conn) ;          
       end
    end
    
end

for i=1:length(msgerror)
   msgerror{1,i} = mat2str(i) + ")" + msgerror{1,i} ; 
end


stat = table(ndeleted, nupdated, ninserted) ; 
newdata = getProduct(conn) ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end % function savegeneraltable

% -------------------------------------------------------

function [idproduct,   msgerror ] = validateProduct(i, conn, data, mmsg, nerror ) 

    msgerror = {} ;
    idproduct = 0 ;
    i = int64(i) ; 
    Action = data.Action(i) ;   
    Product =  strtrim( data.Name(i)) ; 
    Name_coa =  strtrim( data.Name_coa(i)) ; 

    ok = checkNotNull( Product ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, [Action,  nerror, data.id(i), "Name must be not null."] ) ;
       return ; 
    end
    ok = checkNotNull( Name_coa ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, [Action,  nerror, data.id(i), "Name_coa must be not null."] ) ;
       return ; 
    end
    
    if strcmp(Action, "U") && isnan( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), nerror] ) ;
       return 
    end

    idproduct = checkFK( conn, "SELECT id FROM product WHERE name='%s';", Product ) ; 
end 

