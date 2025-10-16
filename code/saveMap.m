% This function saves the excel sheet into the table Map
function [newdata, msgerror, stat, pendingdata] = saveMap(conn, data)

nerror = 1 ; 
pendingdata = table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Map') ; 

if not(isempty(msgerror))
   newdata = getMap(conn) ; 
   return ; 
end

% Formatted string output
mmsg.row = "Action=%s, row %s, id:%s. %s"  ; 
mmsg.ColumnValue = "Action=%s, row %s, id:%s. column:%s value:%s. %s"  ; 
mmsg.Column = "Action=%s, row %s, id:%s. column:%s. %s"  ; 

for i = 1:height(data) 
    Action = strtrim(data.Action(i)) ;
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
   
    ArticleCode =  strtrim( data.ArticleCode(i)) ; 
    LogisticInfo =  strtrim( data.LogisticInfo(i)) ; 
    ok = checkNotNull( LogisticInfo ) ; 
    if not(ok)   
       LogisticInfo = "" ;   
    end        
    
    if ismissing(Product)
       msgerror{ length(msgerror)+1 } =  sprintf( "Action %s, row %s. Product cannot be empty", Action, i) ; 
       data.Action(i) = "*" + Action ; 
       return 
    end

    if ismissing(Quality)
       msgerror{ length(msgerror)+1 } =  sprintf( "Action %s row %s. Quality cannot be empty", Action, i ) ; 
       data.Action(i) = "*" + Action ; 
       return 
    end

    if strcmp( data.Action(i), "D" ) 
       if not( isnan( str2double( data.id(i) ) ))
          sql = "DELETE FROM Map WHERE id =" + data.id(i) + ";"  ; 
          execute(conn,sql) ; 
          commit(conn) ; 
          ndeleted = ndeleted  + 1 ; 
        else
          msgerror{ length(msgerror)+1 } =  sprintf( mmsg.row, [Action,  nerror, data.id(i), " The row can not be deleted." ] ) ; 
          data.Action(i) = "*" + Action ; 
       end
    end % if 

    if strcmp( data.Action(i), "U" ) 
      [ idproduct, idquality,  ~ ,  msgerror2 ] = validateMap(i, conn, data, mmsg, nerror ) ; 
      nerror = nerror + length(msgerror2) ;  
       
      if  isempty(msgerror2)
         id = checkFK( conn, "SELECT id FROM map WHERE id=%s", data.id(i) ) ; 
         if id > 0
          sql = "UPDATE Map SET product_id=%s, quality_id=%s, articlecode='%s', logisticinfo='%s' " + ...
              " WHERE id=%s ;" ; 
          values = [idproduct, idquality,  ArticleCode, LogisticInfo, id] ; 
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
       [ idproduct, idquality,  idmap ,  msgerror2 ] = validateMap(i, conn, data, mmsg, nerror ) ; 

       nerror = nerror + length(msgerror2) ;  
       if not( isempty(msgerror2) ) 
          msgerror = [msgerror, msgerror2 ] ; 
          data.Action(i) = "*" + Action ; 
       end
       if idmap > 0 
          msgerror{ length(msgerror)+1 } = sprintf("Action %s, row %s. The " + ...
              "combination (Product, Quality, LogisticInfo):(%s,%s,%s) already " + ...
              "exists", [Action,nerror, Product, Quality,LogisticInfo] ) ; 
          data.Action(i) = "*" + Action ; 
       end    
       if idmap == 0 && isempty(msgerror2)
          sql = "INSERT into Map(product_id, quality_id, articlecode, logisticinfo) " + ...
              "  values (%s, %s, '%s', '%s');" ; 
          values = [idproduct, idquality,  ArticleCode, LogisticInfo] ;
          sql = sprintf(sql, values ) ; 
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
newdata = getMap(conn) ; 

idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end % function saveMaptable

% -------------------------------------------------------


function [ idproduct, idquality, idmap ,  msgerror ] = validateMap(i, conn, data, mmsg, nerror )

    msgerror = {} ;
    idproduct = 0 ;
    idquality = 0 ;

    i = int64(i) ; 
    Action = strtrim( data.Action(i)) ;
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    LogisticInfo =  strtrim( data.LogisticInfo(i)) ; 
    
    ok = checkNotNull( LogisticInfo ) ; 
    if not(ok)   
       LogisticInfo = "" ;   
    end    
    idmap = 0 ; 

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

    idproduct = checkFK( conn, "Select id From product Where name='%s'", Product  ) ; 
    if idproduct == 0              
       msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Product:"+Product+" does not exist."   ] ) ;
       return ; 
    end

    idquality = checkFK( conn, "Select id From quality Where name='%s'", Quality  ) ; 
    if idquality == 0              
        msgerror{ length(msgerror)+1 } = sprintf( mmsg.row , [Action, nerror, data.id(i),  "Quality:"+Quality+" does not exist."   ] ) ;
       return ; 
    end

    if strcmp(Action, "U") && isnan( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), nerror] ) ;
       return 
    end
    
    % Checking uniqueness of product_id and quality 
    idmap = checkFK( conn, "SELECT id FROM map WHERE product_id=%s and quality_id=%s and logisticinfo='%s';",  [idproduct, idquality, LogisticInfo ]  ) ; 

end % ValidateMap


