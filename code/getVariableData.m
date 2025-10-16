% This function queries the data of a given test parameter
function data = getVariableData( conn, variableName,  idSamplePoint, bruto, idProduct, idQuality)

ddate = datetime  ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdatefin = string( ddate )  ; 

ddate = datetime - 365 ;  
ddate.Format = 'yyyy-MM-dd' ; 
sdateini = string( ddate )  ; 

sColumns = "s.loadingdate date, avg(m.value) value " ; 
sFrom = "measurement m, sample  s, variable v" ; 
sWhere = "s.id=m.sample_id and m.variable_id = v.id and v.shortname = '%s' and m.value !=-1 " + ...
    " and s.loadingdate>='%s' and s.loadingdate<='%s' " ; 
if not( strcmp(bruto, '') )
   sFrom = sFrom + ", product p " ; 
   sWhere = sWhere + " and s.product_id = p.id " + ...
    " and replace( replace(bruto, '<sub>', ''), '</sub>', '')='"+strtrim(bruto)+"' " ; 
end

if idProduct > 0 
   sWhere = sWhere + " and s.product_id= " + string(idProduct) ; 
end

if idQuality > 0 
   sWhere = sWhere + " and s.quality_id= " + string(idQuality) ; 
end

if idSamplePoint > 0 
   sWhere = sWhere + " and s.samplepoint_id= " + string(idSamplePoint) ; 
end

sql = "SELECT " + sColumns + " FROM " + sFrom + " WHERE " + sWhere + " GROUP BY s.loadingdate ORDER BY s.loadingdate" ; 
sql = sprintf(sql ,  variableName, sdateini, sdatefin ) ; 

data = select(conn, sql) ;
data.Properties.VariableNames{2} = variableName ; 
if height(data) > 0 
   %data.date = datetime( string(data.date) + " " + string(data.time) ) ; 
   data.date = datetime( data.date ) ;    
end 

end