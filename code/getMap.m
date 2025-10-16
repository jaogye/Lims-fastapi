function data = getMap(conn)

sql = "SELECT ' ' Action, m.articlecode ArticleCode, p.name Product, m.logisticinfo LogisticInfo, " + ...
    " q.name Quality, m.id id " + ...
    " FROM map m, " + ...
    " product p, quality q" + ...
    " WHERE m.product_id=p.id and m.quality_id=q.id     " + ...
    " ORDER BY p.name, q.name;" ; 

data = select( conn, sql ) ;
%data = table( d.Action, d.Product, d.Quality, d.ArticleCode, d.id ) ;
%data.Properties.VariableNames{1} = 'Action' ; 
%data.Properties.VariableNames{2} = 'Product' ; 
%data.Properties.VariableNames{3} = 'Quality' ; 
%data.Properties.VariableNames{4} = 'ArticleCode' ; 
%data.Properties.VariableNames{5} = 'id' ; 

end
