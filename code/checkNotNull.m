function ok = checkNotNull( value )
ok=1 ; 
value = string(value) ; 
if isa(value, 'string')
   if ismissing(value) || strcmp(strtrim(value), "")
      ok=0 ; 
   end 
 else
   if ismissing(value) 
      ok=0 ; 
   end
end
end % checkNotNull
