function [newdata, msgerror, stat, pendingdata] = saveQuality(conn, data)
% This function checks the validity and updates sample matrix (sample points)

nerror = 1 ; 
pendingdata = table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Quality') ; 

if not(isempty(msgerror))
   newdata = getQuality(conn) ; 
   return ; 
end

% Formatted string output
mmsg.row = "Action=%s, row %s, id:%s. %s"  ; 
mmsg.ColumnValue = "Action=%s, row %s, id:%s. column:%s value:%s. %s"  ; 
mmsg.Column = "Action=%s, row %s, id:%s. column:%s. %s"  ; 

for i = 1:height(data)     
    name =  strtrim( data.Name(i)) ;    
    longname =  strtrim( data.LongName(i)) ;    
    Action = strtrim( data.Action(i)) ;     
    if strcmp( data.Action(i), "D" )        
        msgerror2 = checkChildren(conn, 'Quality' , data.id(i)  ) ; 
        if isempty(msgerror2)                
          sql = "DELETE FROM Quality WHERE id =%s ;"  ; 
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
       [~,   msgerror2 ] = validateQuality(i, conn, data, mmsg, nerror )  ;
       nerror = nerror + length(msgerror2) ;         
       if isempty(msgerror2)  
          id = checkFK( conn, "SELECT id FROM Quality WHERE id=%s", data.id(i) ) ; 
          if id > 0
             sql = "UPDATE Quality SET name='%s', longname='%s' WHERE id=%s ;" ; 
             values = [name, longname, id ] ;  
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
       [idquality,   msgerror2 ] = validateQuality(i, conn, data, mmsg, nerror )  ;
       nerror = nerror + length(msgerror2) ;         
       if not( isempty(msgerror2) ) 
           msgerror = [msgerror, msgerror2 ] ; 
           data.Action(i) = "*" + Action ; 
       end
       if idquality > 0 
          msgerror{ length(msgerror)+1 } = sprintf("Action %s, row %s." + ...
              " Quality:%s already exists", [Action,nerror,  longname] ) ; 
          data.Action(i) = "*" + Action ; 
       end        
       if idquality==0 && isempty(msgerror2)
          sql = "INSERT into Quality(name, longname) values ('%s', '%s' )" ; 
          sql = sprintf(sql, name, longname) ; 
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
newdata = getQuality(conn) ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 


end % function savegeneraltable

% -------------------------------------------------------

function [idquality,   msgerror ] = validateQuality(i, conn, data, mmsg, nerror ) 

    msgerror = {} ;
    idproduct = 0 ;
    i = int64(i) ; 
    Action = data.Action(i) ;
    LongName =  strtrim( data.LongName(i)) ; 
    Name =  strtrim( data.Name(i)) ; 

    ok = checkNotNull( Name ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, [Action,  i, data.id(i), "Name must be not null."] ) ;
       return ; 
    end

    ok = checkNotNull( LongName ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.Column, [Action,  i, data.id(i), "Bruto must be not null."] ) ;
       return ; 
    end

    if strcmp(Action, "U") && isnan( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), nerror] ) ;
       return 
    end

    idquality = checkFK( conn, "SELECT id FROM quality WHERE name='%s';", Name ) ; 

end 


% This function validates the column names of data table
function [ok, msg] = checkQualityTable(data)

cols = [ "Action" , "Name", "LongName" , "id" ] ; 

ok = 1 ; 
msg = "" ; 
for i=1:length(cols)
    if  not ( strcmp( cols{1,i}, data.Properties.VariableNames{i} ))
       msg = "Incorrect order of columns. Expected column: " + cols{1,i} + " but it is received :" + data.Properties.QualityNames{i} ; 
       ok = 0 ;
       return 
    end
end

end
