function  conn = getconn()

if isdeployed==1
  d = load('pvsconnection') ;
  %d = load('serverconnection') ;
else
  d = load('serverconnection') ;
end
conn = odbc(d.dsnless);

return 