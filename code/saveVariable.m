% This function saves the content of the excel sheet of tests (variables) entered by the user 
% to the database (table variable)
% Since SPEC and SAMPLEMATRIX are denormalized tables that contain all
% variables defined in Variable table, this function Insert,Rename or
% delete columns associated with variables(tests) if the variables are
% inserted, modified its name or deleted.
function [newdata, msgerror, stat, pendingdata] = saveVariable(conn, data)
% This function checks the validity and updates sample matrix (sample points)

pendingdata = table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'Variable') ; 

if not(isempty(msgerror))
   newdata = getVariable(conn) ; 
   return ; 
end

% Formatted string output
for i = 1:height(data)     
    Shortname =  strtrim( data.Shortname(i)) ;    
    Test =  strtrim( data.Test(i)) ; 
    Element =  strtrim( data.Element(i)) ; 
    Unit =  strtrim( data.Unit(i)) ; 
    Order =  strtrim(string( data.Ord(i)) ); 
    TypeVar =  strtrim( string( data.TypeVar(i)) ); 
    listvalue =  strtrim( string( data.listvalue(i)) ); 
    Action = data.Action(i) ; 
    if Action == "D" 
        msgerror2 = checkChildren(conn, 'Variable' , data.id(i)  ) ; 
        if isempty(msgerror2)                    
          sql = "DELETE FROM Variable WHERE id =%s ;"  ; 
          sql = sprintf( sql ,data.id(i) ) ; 
          execute(conn,sql) ; 
          % Eliminate the associated columns 
          if TypeVar == "I"             
             %Check if the columns exists 
             if existsColumn(conn, 'spec', "min_" + Shortname)
                execute(conn, "UPDATE spec set min_"+Shortname+ "= NULL") ; 
                execute(conn, "ALTER TABLE spec DROP COLUMN min_"+Shortname) ;
             end 
             if existsColumn(conn, 'spec', "max_" + Shortname)
                 execute(conn, "UPDATE spec set max_"+Shortname+"=NULL") ;
                execute(conn, "ALTER TABLE spec DROP COLUMN max_"+Shortname) ;             
             end

             %if existsColumn(conn, 'samplematrix', Shortname)
             %   execute(conn, "UPDATE samplematrix set has_"+Shortname+ "= NULL") ; 
             %   execute(conn, "ALTER TABLE samplematrix DROP COLUMN has_"+Shortname) ;
             %end 
          else 
             if existsColumn(conn, 'spec', Shortname) 
                execute(conn, "UPDATE spec set "+Shortname+ "= NULL") ;
                execute(conn, "ALTER TABLE spec DROP COLUMN "+Shortname) ;      
             end
             %if existsColumn(conn, 'samplematrix', Shortname) 
             %   execute(conn, "UPDATE samplematrix set "+Shortname+ "= NULL") ;
             %   execute(conn, "ALTER TABLE samplematrix DROP COLUMN "+Shortname) ;      
             %end
             
          end
          commit(conn) ; 
          ndeleted = ndeleted  + 1 ; 
        else
          msgerror = [ msgerror msgerror2 ] ; 
          data.Action(i) = "*" + Action ; 
        end
    end % if 
    
    if Action == "U"        
      msgerror = validateVariable(i, conn, data, msgerror ) ;  
      if not(isempty(msgerror))
         continue
      end 
      id = data.id(i) ;
      sql = sprintf("SELECT shortname old_name FROM variable WHERE id=%s", id) ;  
      T = select(conn, sql) ;
      if height(T) > 0 
        cmd = "UPDATE variable SET Shortname='%s', Test='%s', Element='%s', Unit='%s' ,ord=%s WHERE id = %s" ; 
        values = [ Shortname, Test, Element, Unit, Order, id  ] ;  
        cmd = sprintf(cmd, values) ;         
        msgerror = updateListValue(conn, id, listvalue, data, i,  msgerror) ; 
        if not(isempty(msgerror))
           msgerror{ length(msgerror) } = sprintf("Action U id=%s .", id ) + msgerror{ length(msgerror) } ; 
        end    
        execute(conn,cmd) ; 
        % Rename of columns 
        if TypeVar == "I"
           execute(conn, "EXEC sp_rename 'spec.min_"+ T.old_name(1) + "', 'min_"+ Shortname + "', 'COLUMN'" );          
           execute(conn, "EXEC sp_rename 'spec.max_"+ T.old_name(1) + "', 'max_"+ Shortname + "', 'COLUMN'" );       
        else    
           execute(conn, "EXEC sp_rename 'spec."+ T.old_name(1) + "', '"+ Shortname + "', 'COLUMN'" );
        end 
        execute(conn, "EXEC sp_rename 'samplematrix.has_"+ T.old_name(1) + "', 'has_"+ Shortname + "', 'COLUMN'" );
        nupdated = nupdated + 1 ; 
        commit(conn) ;   
      else           
          msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s, row %s. The id=%s value is not valid.", ...
              [data.Action(i), i, data.id(i)] ) ; 
          data.Action(i) = "*" + Action ;           
      end 
       
    end        
   if Action == "I"
      msgerror = validateVariable(i, conn, data, msgerror )  ; 
      if not(isempty(msgerror))
         continue
      end 
      sql = "INSERT into variable(shortname, test, element, unit, typevar, ord) values ('%s','%s','%s','%s', '%s', %s )" ; 
      values = [Shortname, Test, Element, Unit, TypeVar, Order ] ;  
      sql = sprintf(sql, values) ; 
      execute(conn,sql) ; 
      T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
      id = T.x(1) ; 
      updateListValue(conn, id, listvalue, data, i,  msgerror) ; 
      dml_spec = "ALTER TABLE SPEC ADD " ;      
      if TypeVar == "I" 
         dml_spec = dml_spec + "min_" + Shortname + " char(15) "+ "max_" + Shortname + " Numeric(12,6) " ;          
      else
         dml_spec = dml_spec + Shortname + " char(1) " ;  
      end      
      dml_samplematrix = "ALTER TABLE samplematrix ADD has_" + Shortname + " tinyint " ; 
      execute(conn, dml_spec) ;    
      execute(conn, dml_samplematrix) ; 

      ninserted = ninserted + 1 ; 
      commit(conn) ;          
    end 
end

for i=1:length(msgerror)
   msgerror{1,i} = mat2str(i) + ")" + msgerror{1,i} ; 
end

stat = table(ndeleted, nupdated, ninserted) ; 
newdata = getVariable(conn) ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end %

function msgerror = validateVariable(i, conn, data, msgerror_old ) 

msgerror = msgerror_old ; 
Shortname =  strtrim( data.Shortname(i)) ;    
Order =  strtrim(string( data.Ord(i)) ); 
TypeVar =  strtrim( string( data.TypeVar(i)) ); 
listvalue =  strtrim( string( data.listvalue(i)) ); 
Action = data.Action(i) ; 
ok = checkNotNull( Order ) ; 
if not(ok)      
   msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, id:%s: %s" , ...
   [Action,  i, data.id(i), "Order column must be not null."] ) ;
   data.Action(i) = "*" + Action ;    
   return  
end 

if Action == "I"
   nid = checkFK( conn, "SELECT * FROM variable where shortname ='%s' ;",  Shortname ) ;       
   if nid > 0 
      msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, id:%s. column:%s. %s" , ...
      [Action,  i, data.id(i), "Repetitive variable:" + Shortname] ) ;
      data.Action(i) = "*" + Action ;    
      return 
   end
end 
ok = checkNotNull( TypeVar ) ; 
if not(ok)      
   msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, id:%s. column:%s. %s", ...
   [Action,  i, data.id(i), "TypeVar must be not null."] ) ;
   data.Action(i) = "*" + Action ; 
end
ok = checkValueList( TypeVar, "L,I" ) ;     
if not(ok)      
   msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, id:%s. column:%s. %s", ...
       [Action,  i, data.id(i), "TypeVar must be '(L)ist' or (I)nterval"] ) ;
   data.Action(i) = "*" + Action ; 
end

ok = checkValueList( TypeVar, "L,I" ) ;     
if not(ok)      
   msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, id:%s. column:%s. %s", ...
   [Action,  i, data.id(i), "TypeVar must be '(L)ist' or (I)nterval"] ) ;
   data.Action(i) = "*" + Action ; 
end

if TypeVar == "L"
   ok = checkNotNull( listvalue ) ; 
   if not(ok)      
      msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s, Shortname:%s: %s", ...
      [Action,  i, Shortname, "listvalue column must be not null."] ) ;
      data.Action(i) = "*" + Action ; 
   end 
end 


end

function msgerror = updateListValue(conn, id, listvalue, data, index, msgerror) 

% Tokenize the string listvalue
tt = strsplit(listvalue, ',');
for i=1:length(tt)
    tt{i} = strtrim(tt{i}) ; 
end
id = string(id) ; 
for i=1:length(tt)
    description = strtrim( tt{i} ) ; 
    sql2 = sprintf("SELECT * FROM listvalue WHERE variable_id=%s AND description='%s'", id, description) ; 
    T = select(conn, sql2) ;
    if height(T) == 0
       execute(conn, sprintf("INSERT INTO listvalue(variable_id, description) VALUES(%s, '%s')", id, description) )
    end     
end

Action = data.Action(index) ; 
if Action == "U"
   % Delete of description that does not exist in listvalue
   T = select(conn, sprintf("SELECT * FROM listvalue WHERE variable_id=%s", id)) ;
   for i=1:height(T)
       des = strtrim(T.description(i)) ; 
       des = des{1} ; 
       idx_value = string(T.id(i)) ;
       idx = -1 ; 
       for j=1:length(tt)
          if strcmp( tt{j}, des)  
             idx = j ;
          end    
       end
       % id_value does not exist in the current listvalue
       if idx == -1 
           msgerror2 = checkChildren(conn, 'Listvalue' , idx_value  ) ; 
           if isempty(msgerror2)                  
               execute(conn, sprintf("DELETE FROM listvalue WHERE id=%s", idx_value)) ;
           else             
             msgerror = [ msgerror msgerror2 ] ; 
             data.Action(index) = "*" + Action ; 
           end
       end 
   end     
end

end

