% This function saves the excel sheet into the table Holidays
function [newdata, msgerror, stat, pendingdata] = saveHolidays(conn, data)
nerror = 1 ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
pendingdata = table() ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Holidays') ; 

if not(isempty(msgerror))
   newdata = getHolidays(conn) ; 
   return ; 
end
	
for i = 1:height(data)    
    Action = strtrim(data.Action(i)) ;
    sdate =  strtrim( data.Date(i)) ; 
    if strlength( sdate ) == 11
        try
           dd =  datetime( data.Date(i) ) ; 
        catch    
          msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s, row %s. Date format is not valid %s .", ...
              [data.Action(i), i, sdate] ) ; 
          data.Action(i) = "*" + Action ; 
          nerror = nerror + 1 ;   
          continue ;             
        end 
        dd.Format = 'yyyy-MM-dd' ; 
        sdate = string(dd) ; 
    end 

    if not( strlength( sdate ) == 10 ) 
       msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s, row %s. Date format is not valid %s .", ...
              [data.Action(i), i, sdate] ) ; 
          data.Action(i) = "*" + Action ; 
          nerror = nerror + 1 ;   
          continue ; 
    end 

    description =  strtrim( data.Description(i)) ; 
    if strcmp( Action, "D" ) 
       if not( isnan( str2double( data.id(i) ) ))
          sql = "DELETE FROM Holidays WHERE date= '%s';"   ; 
          sql = sprintf(sql, sdate) ; 
          execute(conn,sql) ; 
          commit(conn) ; 
          ndeleted = ndeleted  + 1 ; 
       else
          msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s, row %s. The id (=%) value is not valid.", ...
              [data.Action(i), i, data.id(i)] ) ; 
          data.Action(i) = "*" + Action ; 
          nerror = nerror + 1 ; 
       end
    end % if 

    if strcmp( Action, "U" ) 
       sql = "UPDATE holidays SET description='%s' WHERE date='%s' ;" ; 
       sql = sprintf(sql, [description, sdate] ) ; 
       execute(conn,sql) ; 
       commit(conn) ; 
       nupdated = nupdated + 1 ;          
    end

    if strcmp( data.Action(i), "I" ) 
        try
          nid = checkFK( conn, "SELECT * FROM holidays WHERE date ='%s';", sdate ) ;       
        catch e 
            msgerror{ length(msgerror)+1 } = sprintf("Error Identifier: %s Messsage:%s",[e.identifier, e.message] ) ;             
            return ; 
        end
       if nid > 0
          msgerror{ length(msgerror)+1 } = sprintf(  "Row %d. Holiday %s is duplicated " ,  nerror, sdate  ) ;  
          data.Action(i) = "*" + Action ; 
          nerror = nerror + 1 ;           
         else
          sql = "INSERT INTO holidays (date,description) values ('%s', '%s')" ; 
          sql = sprintf(sql, [sdate,  description]) ; 
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
newdata = getHolidays(conn) ; 


end % function savegeneraltable

% -------------------------------------------------------

