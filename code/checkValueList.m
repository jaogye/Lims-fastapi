function ok = checkValueList(  value, list )
ok=1 ; 
if ismissing(value) || strcmp( value, "")
   return ; 
end
k = strfind(list,value) ; 
if isempty(k) 
   ok=0 ; 
end
end % checkNotNull