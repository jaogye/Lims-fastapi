% This function get the pending mesuarements from Lab Samples 
function [summary, detail] = getPendingJobs(conn, sdate )

sql = "Select s.SampleNumber, s.loadingdate,  m.variable, min, max "+...
" FROM measurement m, sample s " + ...
" WHERE  m.sample_id=s.id  and value = -1 and substring(s.loadingdate,1,10)='%s'" + ...
"  ORDER by s.SampleNumber ; " ;   
sql = sprintf( sql, sdate) ; 
detail = select( conn, sql ) ;

detail.Properties.VariableNames{1} = 'SampleNumber' ; 
detail.Properties.VariableNames{2} = 'Date' ; 
detail.Properties.VariableNames{3} = 'Variable' ; 
detail.Properties.VariableNames{4} = 'Min' ; 
detail.Properties.VariableNames{5} = 'Max' ; 
detail.SampleNumber = strtrim(string(detail.SampleNumber)) ; 
detail.Date = strtrim(string(detail.Date) ); 

sql = "SELECT s.samplenumber, count(*) tested FROM sample s, measurement m  " + ...
    " WHERE substring(s.loadingdate,1,10)='%s' and m.sample_id = s.id and m.value > -1 GROUP BY s.samplenumber " + ...
    "UNION " + ...
    "SELECT s.samplenumber, 0 tested FROM sample s WHERE substring(s.loadingdate,1,10)='%s' and NOT " + ...
    " EXISTS(SELECT * FROM measurement m WHERE m.sample_id = s.id and m.value > -1 );" ;   
sql = sprintf( sql, [sdate, sdate]) ; 
T1 = select( conn, sql ) ;

sql = "SELECT s.typesample, s.samplenumber,  sp.name samplepoint, concat(s.loadingdate,' ', s.time) date, " + ...
    "s.customer, p.name product, " + ...
    " q.name quality, count(*) total  " + ...
    " FROM sample s left outer join samplepoint sp on sp.id=s.samplepoint_id, " + ...
    " measurement m,  product p, quality q  " + ...
    " WHERE substring(s.loadingdate,1,10)='%s' and  m.sample_id = s.id  and s.product_id=p.id " + ...
    " and s.quality_id=q.id " + ...
    "GROUP BY s.typesample, s.samplenumber,  sp.name, s.loadingdate, s.time, s.customer, p.name, q.name ;" ; 
    
sql = sprintf( sql, sdate) ; 
T2 = select( conn, sql ) ;

sql = "SELECT s.samplenumber, count(*) notested FROM sample s, measurement m  " + ...
    "WHERE substring(s.loadingdate,1,10)='%s' and m.sample_id = s.id and m.value = -1 GROUP BY s.samplenumber " + ...
    "UNION SELECT s.samplenumber, 0 notested FROM sample s WHERE substring(s.loadingdate,1,10)='%s' and " + ...
    " NOT EXISTS(SELECT * FROM measurement m WHERE m.sample_id = s.id and m.value = -1 ) ;" ;   
sql = sprintf( sql, [sdate, sdate]) ; 
T3 = select( conn, sql ) ;

T4 = outerjoin(T1, T2) ; 
T4.Properties.VariableNames{1} = 'samplenumber';
T = outerjoin( T4 , T3) ; 
T.Properties.VariableNames{1} = 'samplenumber';

summary = table( T.typesample, strtrim(T.samplenumber), strtrim(T.samplepoint), T.date, ...
    strtrim(T.customer), strtrim(T.product), strtrim(T.quality), T.total,  T.tested, T.notested ) ; 

summary.Properties.VariableNames{1}= 'TypeSample' ; 
summary.Properties.VariableNames{2}= 'SampleNumber' ; 
summary.Properties.VariableNames{3}= 'SamplePoint' ; 
summary.Properties.VariableNames{4}= 'SampleDate' ; 
summary.Properties.VariableNames{5}= 'Customer' ; 
summary.Properties.VariableNames{6}= 'Product' ; 
summary.Properties.VariableNames{7}= 'Quality' ; 
summary.Properties.VariableNames{8}= 'Vars.' ; 
summary.Properties.VariableNames{9}= 'Tested' ; 
summary.Properties.VariableNames{10}= 'NotTested' ; 
summary = sortrows(summary, 10, 'descend') ; 

end
