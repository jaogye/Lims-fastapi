function [newdata, msgerror, stat, pendingdata] = saveSampleMatrix(conn, data)
% This function checks the validity and updates sample matrix (sample points)

pendingdata=table() ; 
ndeleted = 0; 
nupdated = 0 ; 
ninserted = 0 ; 
data.Action = upper( data.Action ) ; 
stat = table(ndeleted, nupdated, ninserted) ; 
[msgerror, data] = preProcData( conn, data, 'SampleMatrix') ; 

if not(isempty(msgerror))
   newdata = getSampleMatrix(conn) ; 
   return ; 
end

[indexCols, tests, msgerror] = getDataVariables(conn, data, msgerror) ; 
if not(isempty(msgerror))
   newdata = getSpec(conn, 'GEN') ; 
   return ; 
end

% Formatted string output
mmsg.notiddelete  = "Action=D. In row %s The id=%s (the last column) of the combination of %s is not correct. The row is not deleted." ; 
mmsg.notokvarible = "Action=%s. In row %s, the (column,value) (%s,%s) reason=%s"  ; 
mmsg.notNull = "Action=%s. In row %s, the column %s must be not null " ; 

for i = 1:height(data) 
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    SamplePoint =  strtrim( data.SamplePoint(i)) ; 
    ok = checkNotNull( SamplePoint ) ;
    if not(ok)      
       SamplePoint = "" ;  
    end    
    Frequency =  strtrim( data.Frequency(i)) ;
    Action = strtrim( data.Action(i)) ; 
    if strcmp( data.Action(i), "D" ) 
       if not( isnan( str2double( data.id(i) ) ))
          msgerror2 = checkChildren(conn, 'SampleMatrix' , data.id(i)  ) ; 
          if isempty(msgerror2)
             sql = "DELETE FROM samplematrix WHERE id =%s;"  ;
             sql = sprintf(sql, data.id(i)) ; 
             execute(conn,sql) ; 
             commit(conn) ; 
             ndeleted = ndeleted  + 1 ;              
          else 
             msgerror = [ msgerror msgerror2 ] ; 
             data.Action(i) = "*" + Action ; 
          end
        else
          msgerror{ length(msgerror)+1 } =  sprintf( "Action=%s, row %s. " + ...
              "The id=%s (the last column) is " + ...
              "not correct. The row is not deleted." , Action, i, data.id(i) ) ; 
          data.Action(i) = "*" + Action ; 
       end
    end % if 

    if strcmp( data.Action(i), "U" )       
      [idsamplepoint, idproduct, idquality, idspec, ~, flags,  msgerror2 ] = validateSampleMatrix(i, conn, data, tests, indexCols, mmsg ); 
      if isempty(msgerror2)
          idsamplematrix = checkFK( conn, "SELECT id FROM samplematrix WHERE id=%s", data.id(i) ) ; 
          if idsamplematrix > 0          
             if strcmp(SamplePoint, ''  ) 
                cols = [ "product_id", "quality_id", "spec_id", "Frequency"] ; 
                reg = { idproduct, idquality, idspec, data.Frequency(i)  } ; 
             else
                cols = [ "product_id", "quality_id", "spec_id", "SamplePoint_id", "Frequency"] ; 
                reg = { idproduct, idquality, idspec, idsamplepoint, data.Frequency(i)  } ;              
             end 
             sql = getupdateSampleMatrix(idsamplematrix, cols, reg ,flags, tests)  ; 
             execute(conn,sql) ; 
             commit(conn) ; 
             nupdated = nupdated + 1 ; 
             updatedSampleMatrix(conn, idsamplematrix , flags, tests) ;              
          else 
            msgerror2{ length(msgerror2)+1 } = sprintf("Action %s, row %s. " + ...
               "Invalid id=%s. Upload this file with the lastest version. The row is not updated.", ...
               [Action, i, data.id(i)] ) ; 
            data.Action(i) = "*" + Action ; 
          end 
      else
         msgerror = [msgerror, msgerror2 ] ;    
         data.Action(i) = "*" + Action ; 
      end
    end

    if strcmp( data.Action(i), "I" ) 
       [idsamplepoint, idproduct, idquality, idspec, idsamplematrix, flags,  msgerror2 ] = validateSampleMatrix(i, conn, data, tests, indexCols, mmsg )  ;
       if not( isempty(msgerror2) ) 
          msgerror = [msgerror, msgerror2 ] ; 
          data.Action(i) = "*" + Action ; 
       end
       if idsamplematrix > 0 
          msgerror{ length(msgerror)+1 } = sprintf("Action=%s, row %s. " + ...
              "The combination (Product, Quality, SamplePoint, Frequency):(%s,%s,%s,%s) " + ...
              "already exists", [data.Action(i), i, Product, Quality, SamplePoint, Frequency] ) ; 
          data.Action(i) = "*" + Action ; 
       end    
       if idsamplematrix == 0 && isempty(msgerror2)
          if strcmp(SamplePoint, ''  )  
             cols = [ "product_id", "quality_id", "spec_id", "Frequency"] ;           
             reg = { idproduct, idquality, idspec, Frequency  } ; 
            else
             cols = [ "product_id", "quality_id", "spec_id", "SamplePoint_id", "Frequency"] ;           
             reg = { idproduct, idquality, idspec, idsamplepoint , Frequency  } ; 
          end 
          sql = getinsertSampleMatrix(cols, reg ,flags, tests) ;
          execute(conn,sql) ; 
          ninserted = ninserted + 1 ;            
          T = select(conn,'SELECT SCOPE_IDENTITY() ;') ; 
          idsamplematrix = T.x(1) ; 
          updatedSampleMatrix(conn, idsamplematrix, flags, tests) ;
          commit(conn) ; 
       end
    end
end

for i=1:length(msgerror)
   msgerror{1,i} = mat2str(i) + ")" + msgerror{1,i} ; 
end

stat = table(ndeleted, nupdated, ninserted) ; 
newdata = getSampleMatrix(conn) ; 
idx = data.Action == "*I" | data.Action == "*D" | data.Action == "*U" ; 
pendingdata = data(idx, :) ; 

end % function savegeneraltable

% -------------------------------------------------------
         
function [idsamplepoint, idproduct, idquality, idspec, idsamplematrix, flags,  msgerror ] = validateSampleMatrix(i, conn, data, tests, indexCols,  mmsg )
    
    msgerror = {} ;
    flags = {}  ;
    idproduct = 0 ;
    idquality = 0 ;
    idspec = 0 ;    
    idsamplematrix = 0 ;
    idsamplepoint = 0 ;
    Action = data.Action(i) ;
    Product =  strtrim( data.Product(i)) ; 
    Quality =  strtrim( data.Quality(i)) ; 
    SamplePoint =  string( strtrim( data.SamplePoint(i)) ); 
    Frequency =  string( strtrim( data.Frequency(i)) ); 
    ok = checkNotNull( SamplePoint ) ; 
    if not(ok)  
       SamplePoint = "" ;  
    end     
    ValidFrequency = "1/2 year,Batch, Batch - loading,Day,Delivery,Month,Quarter,Week,Day - loading"; 

    ok = checkNotNull( Product ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.notNull, [Action,  i, "Product"] ) ;
       return ; 
    end
    
    ok = checkNotNull( Quality ) ; 
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  mmsg.notNull, [Action, i, "Quality"] ) ;
       return ; 
    end

    ok = checkNotNull( SamplePoint ) ; 
    if not(ok) && not( strcmpi(Frequency, "Batch") )
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. Frequency=%s then SamplePoint:%s must not be null", ...
           [Action, i, Frequency, SamplePoint] ) ;
       return ; 
    end


    idproduct = checkFK( conn, "SELECT id from product where name='%s';",  Product  ) ; 
    if idproduct == 0
       msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s, row %s. Product %s is not found in table product." , [Action, i , Product]  ) ;
       return ; 
    end

    idquality = checkFK( conn, "SELECT id from quality where name='%s';",  Quality  ) ; 
    if idquality == 0
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. Quality %s is not found in table quality." , [Action, i , Quality]  ) ;
       return ; 
    end
    idproduct = string(idproduct) ; 
    idquality = string(idquality) ; 
    idspec = checkFK( conn, "SELECT id from spec where typespec='GEN' and product_id=%s and quality_id=%s;",  [idproduct, idquality] ) ; 
    if idspec == 0
       msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. The combination of (Product,Quality):(%s,%s) is not found in table Spec." , [Action, i , Product, Quality]  ) ;
       return ; 
    end
    
    if strcmp(Action, "U") && isnan( str2double( data.id(i) ))               
       msgerror{ length(msgerror)+1 } = sprintf("Action=%s, " + ...
            "row %s. id must be Integer. ", [data.Action(i), i] ) ;
       return ;
    end    

    if not( strcmp( SamplePoint, "") ) 
      idsamplepoint = checkFK( conn, "SELECT id from samplepoint where name='%s';",  SamplePoint  ) ; 
      if idsamplepoint == 0
         msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, row %s. SamplePoint %s is not found " + ...
             " in table SamplePoint." , [Action, i , SamplePoint]  ) ;
         return ; 
      end
    end

    ok = checkValueList( Frequency, ValidFrequency ) & checkNotNull( Frequency ) ;
    if not(ok)      
       msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s. In row %s, the column " + ...
           "%s (%s) must contains one of these values %s " , ...
           [ Action, i, "Frequency", Frequency, ValidFrequency ] ) ;
       return ; 
    end
    
    if strcmp( SamplePoint, '')  
        idsamplematrix =checkFK( conn, "SELECT id from samplematrix where  " + ...
          "product_id=%s and quality_id=%s and samplepoint_id is null and frequency='%s'; " , ...
          [string(idproduct), string(idquality), Frequency] ) ;    
    else 
        idsamplematrix =checkFK( conn, "SELECT id from samplematrix where  " + ...
          "product_id=%s and quality_id=%s and samplepoint_id=%s and frequency='%s'; " , ...
          [string(idproduct), string(idquality), idsamplepoint, Frequency] ) ;    
    end
    for j=1:height(tests)
        varname =  tests{j,2} ; 
        ok = checkValueList(  data{i,indexCols{j}}, "x,X,xx,XX" );
        if ok 
           flags{j} = 0 ; 
           if strcmpi( data{i,indexCols{j}}, "X" )  
               flags{ j } = 1 ;
           end 
           if strcmpi( data{i,indexCols{j}}, "XX" )  
               flags{ j } = 2 ;
           end                
         else
           msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s. In row %s, " + ...
               "the column %s must contains one of these values %s " , ...
               [ Action, i, varname, "x,X,xx,XX"] ) ;
           return ; 
        end 

    end             

end % ValidateSampleMatrix


% ----------------------------------------------------------------------------------------
% ----------------------------------------------------------------------------------------


function  sql = updatedSampleMatrix(conn, idsamplematrix, flags, tests)

sql = "DELETE FROM dsamplematrix WHERE samplematrix_id=%s ; "; 
sql = sprintf(sql, string(idsamplematrix) ) ; 
execute(conn, sql);

for i = 1:length(flags)  
    if flags{i} && tests{i,1} > 0
       sql = "INSERT dSampleMatrix(samplematrix_id, variable_id, ord) VALUES( %s,%s, %s) ; "; 
       sql = sprintf(sql , [ string(idsamplematrix), tests{i,1}, flags{i} ]) ; 
       execute(conn, sql);
    end
end % for

commit(conn) ; 
end 


function  sql = getinsertSampleMatrix(cols, reg ,flags, tests) 

sql = "INSERT into samplematrix(" + cols{1,1} ;  
for i = 2:length(cols)  
    if not (ismissing( reg{1,i} ))
       sql = sql +"," + cols{1,i} ; 
    end
end % for
for i = 1:height(tests)  
    if not (ismissing( flags{i} )) 
       sql = sql +"," + "has_" + tests{i,2} ; 
    end
end % for

if strcmp( class(reg{1,1}), "double" ) || strcmp( class(reg{1,1}),  "int32") 
   sql = sql +") values( " + mat2str(reg{1,1}) ;
 else
   sql = sql +") values( '" + reg{1,1} + "'";
end      

for i = 2:length(reg)  
  if not (ismissing( reg{1,i} ))
    if strcmp( class(reg{1,i}), "double" )  || strcmp( class(reg{1,i}),  "int32") 
       sql = sql +", " + mat2str(reg{1,i}) ;
      else
       sql = sql +", '" + reg{1,i} + "'";
     end      
   end 
end

for i = 1:length(flags)  
    if flags{i} == 1 
       sql = sql +", 1" ;
    end   
    if flags{i} == 2 
       sql = sql +", 2" ;
    end   
    if not(flags{i}==1) && not(flags{i}==2)
       sql = sql +", 0" ; 
    end
end % for
sql = sql + ");" ; 

end 



function  sql = getupdateSampleMatrix(id, cols, reg ,flags, tests) 

sql = "UPDATE samplematrix SET " + cols{1,1} + "=";  
if strcmp( class(reg{1,1}), "double" ) 
   sql = sql + mat2str(reg{1,1}) ;
 else
   sql = sql + "'" + reg{1,1} + "'";
end      

for i = 2:length(cols)  
    sql = sql +"," + cols{1,i} + "=";
    if ismissing( reg{1,i} ) 
       sql = sql + "NULL" ; 
     else      
      if strcmp( class(reg{1,i}), "double" ) || strcmp( class(reg{1,i}),  "int32") 
         sql = sql + mat2str(reg{1,i}) ;
       else
         sql = sql + "'" + reg{1,i} + "'";
      end      
    end
end % for

for i = 1:height(tests)  
    sql = sql +"," + "has_" + tests{i,2} + "=";
    if flags{i} == 1 
       sql = sql +" 1" ;
    end   
    if flags{i} == 2 
       sql = sql +" 2" ;
    end   
    if not(flags{i}==1) && not(flags{i}==2)
       sql = sql +" 0" ; 
    end


end % f3or

sql = sql + " WHERE id = " + id + ";" ;

end 



