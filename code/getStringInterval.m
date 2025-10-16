function s = getStringInterval( x1, x2 )
    s = ''   ; 
    s1 = '' ; 
    if not( isnan( x1 ))
       s1 =  num2str( x1 ) ;
    end 
    s2 = '' ; 
    if not( isnan( x2 ))
       s2 =  num2str( x2 )  ;
    end
    s = strcat(s1,  '-' , s2 ) ;
    if x1 == 0 & x2 == 0  ; 
       s = 'x' ; 
    end
    if isnan(x1) & isnan(x2)
       s = '' ; 
    end
end