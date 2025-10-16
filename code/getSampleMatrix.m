function data = getSampleMatrix(conn)

cols = varColumns(conn, 'db.samplematrix' ) ; 
scols = cols{1} ; 
for i = 2:length(cols)
    scols = scols + "," + cols{i}  ; 
end

sql = "SELECT "+scols+" FROM samplematrix s left join " + ...
    "samplepoint sp on s.samplepoint_id=sp.id, product p, quality q " ...
     + "WHERE s.product_id=p.id AND s.quality_id=q.id " + ...
     " ORDER BY Product, Quality, sp.name ; " ; 

d = select( conn, sql ) ;

dd = table( d.Action, d.Product, d.Quality, d.SamplePoint, d.Frequency, d.Visual ) ;

dd.Properties.VariableNames{1} = 'Action' ;                                
dd.Properties.VariableNames{2} = 'Product' ;                                                             
dd.Properties.VariableNames{3} = 'Quality' ;                                                 
dd.Properties.VariableNames{4} = 'SamplePoint' ;                            
dd.Properties.VariableNames{5} = 'Frequency' ;              
dd.Properties.VariableNames{6} = 'Visual' ;         

if height(d) == 0
   data = dd ; 
   return  
end   
[indexCols, tests, ~] = getSampleMatrixVariables(conn, d) ; 
x = {} ; 
for i=1:height(d)
   for j=1:height(tests)
      switch d{i,indexCols{j,1}} 
        case 1
          x{i,j} = 'X' ;   
        case 2 
          x{i,j} = 'XX' ;   
        otherwise
          x{i,j} = '' ; 
      end     
   end
end 

tx = cell2table(x) ; 
for i = 1:height(tests)
    tx.Properties.VariableNames{i} = tests.shortname{i};
end

id = table(d.id ) ;
id.Properties.VariableNames{1} = 'id' ; 

data = [dd, tx, id ] ; 

end
