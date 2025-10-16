function sdate = getCurrentDate()

dd =datetime ; 
dd.Format = 'yyyy-MM-dd HH:MM:SS' ; 
dd=string(dd) ; 
sdate = extractBetween(dd,1,10 ) ; 

end 