% This functon counts the number of specifications from limits
function  n = countSpec( limits)
n = 0 ; 
for i = 1:length(limits)      
    if isstring( limits{1,i}(1) )
       n=n+1 ; 
    else   
      smin="null" ; 
      if not (isnan( limits{1,i}(1)) )
         smin = mat2str( limits{1,i}(1) ) ; 
      end
      smax = "null" ; 
      if not (isnan( limits{1,i}(2)) )
         smax = mat2str( limits{1,i}(2) ) ;         
      end
      if not( strcmp (smin, 'null') ) || not( strcmp(smax, 'null') ) 
         n=n+1 ; 
      end
    end
end % for
end 
