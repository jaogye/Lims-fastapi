% This function extracs the intervals from an excel two of the sheet inputted by the user in tables Customer
%List or GeneralList
function  [limits, msgerror] = getLimits(conn, typespec, data, tests, indexCols, msgerror, index)

limits = {} ;    
for j = 1:height(tests)
    test = string( tests{j,2} ); 
    value = strrep( data{index, indexCols{j} } , ",", "." )  ; 
    interval = [nan, nan] ; 
    msg = "" ; 
    if tests{j,3} == "I"
      [ interval, msg ] = getInterval(value) ; 
      if not(strcmp(msg, ""))
         msgerror{ length(msgerror)+1 } = sprintf( "Action=%s, id %s. Column:%s value:%s. %s", ...
               [ data.Action(index),  data.id(index), test, data{index, indexCols{j} } ,  msg ]  ) ;
         return ; 
      end
    else
      ok = checkNotNull(value) ; 
      if ok
         ok = checkValueList(value, "Y,X")  ;
         if not(ok)
            msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s, row %s. Column:%s Invalid value:%s. %s", ...
                  [ data.Action(index), data.id(index) , test, value ,  msg ]  ) ;
            return ; 
         end  
         interval = [value, nan] ; 
      end       
    end

    switch typespec
      case 'CLI'   
        % If the user typed X 
        if not(isstring(interval(1)) ) && (interval(1) == 0) && (interval(2) == 0) 
           Quality =  strtrim( data.Quality(index)) ; 
           Product =  strtrim( data.Product(index)) ; 
           idproduct = checkFK( conn, "SELECT id FROM product WHERE name='%s';",  Product  ) ; 
           idquality = checkFK( conn, "SELECT id from quality where name='%s' ;",  Quality  ) ;  
           sql = "SELECT id, min_%s v1, max_%s v2 FROM spec where typespec='GEN' and product_id=%s  and quality_id=%s ;"     ; 
           sql = sprintf(sql, [test, test, idproduct, idquality] ) ;
           T = select(conn, sql) ; 
           if height(T)==0
              msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s, row %s. column:%s value:%s. %s" , ...
                  [ data.Action(index), data.id(index), test, data{index,indexCols{j} } ,  ...
                  " The corresponding interval is not found in table Spec." ]  ) ;
              return ; 
           else       
             if checkNotNull( T.v1 ) || checkNotNull( T.v2 )
                interval(1) = T.v1 ; 
                interval(2) = T.v2 ; 
             else                
                msgerror{ length(msgerror)+1 } = sprintf( ...
                  "Action=%s, row %s. The combination (Product,Quality)" + ...
                  "=(%s,%s) on column:%s in table Spec has a null interval. Hence the value:%s cannot be resolved.", ...
                  [ data.Action(index), data.id(index), Product, Quality, test, data{index, indexCols{j} }  ]  ) ;
                return ; 
             end   
           end 
        end
      case 'GEN'
        % If the user typed X 
        if not(isstring(interval(1)) ) && (interval(1) == 0) && (interval(2) == 0) 
            ss = sprintf(  "Action %s, row:%s, id:%s, Column:%s. The X value " + ...
                "is not valid for Spec Table." , [ data.Action(index), data.id(index), data.id(index), test]   ) ; 
            msgerror{ length(msgerror)+1 } = ss ; 
            return ; 
        end
        if not(strcmp(msg, ""))     
           msgerror{ length(msgerror)+1 } = sprintf(  "Action=%s, row %s. Column:%s value:%s. %s", ...
               [ data.Action(index), data.id(index), test, data{index,indexCols{j}} ,  msg ]  ) ;           
           return ; 
        end
    otherwise
        warning('Unexpected type specification.')        
    end
    limits{ length(limits)+1} = interval ; 
end 

end  % getlimits