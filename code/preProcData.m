% This function validates the excel sheet input data 
function [msgerror, data] = preProcData( conn, data, tableType)

colNames = getColNames(conn, tableType) ; 
data.Action = upper( data.Action ) ; 
msgerror = {} ; 

% Validation of the column names
[ok, msg] = checkDataCols(data, colNames) ;
if not(ok)
   msgerror{1} = msg ;     
   return ; 
end

data.Action = upper(data.Action) ;
% Validation of Action column
idx = not(data.Action == "I") & not(data.Action == "D") & not(data.Action == "U") & not(ismissing(data.Action)) & not(strlength(data.Action) == 0) ; 
dd = data(idx, :) ; 
if height(dd) > 0
   msgerror{1} = sprintf( "There are %d rows with wrong values in column Action", [height(dd)] ) ;     
   return ; 
end

%data.('row') = zeros( [1,height(data)] )' ; 
%for i=1:height(data)
%    data.row(i) = i+1; 
%end
data.Action = upper(data.Action) ;
idx = data.Action == "I" | data.Action == "D" | data.Action == "U" ; 
data = data(idx, :) ; 

end

%This function preprocess the data of master tables 
function cols = getColNames(conn, tableType) 
cols = [] ; 
switch tableType
    case 'CustomerList'
        cols = varColumns(conn, 'tbl.customerlist' ) ; 
    case 'SampleMatrix'
        cols = varColumns(conn, 'tbl.samplematrix' ) ; 
    case 'Spec'
        cols = varColumns(conn, 'tbl.spec' ) ;  
    case 'Product'
       cols = [ "Action" , "Name" , "Bruto", "Name_coa", "id" ] ;  
    case 'Quality'
       cols = [ "Action" , "Name", "LongName" , "id" ] ;  
    case 'Map' 
        cols = [ "Action" , "ArticleCode", "Product" , "LogisticInfo" , "Quality", "id" ] ; 
    case 'SamplePoint'
       cols = [ "Action" , "Name" , "id" ] ;      
    case 'Holidays'
       cols = [ "Action" , "Date" , "Description" ] ; 
    case 'Variable'
       cols = [ "Action" , "Shortname" , "Test" , "Element", "Unit", "Ord", "TypeVar", "listvalue", "id" ] ;   
end 

end


