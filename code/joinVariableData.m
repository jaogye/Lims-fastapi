% This function makes the outjoin of adata{1}, adata{2}, ... 
% This function is used in dashboard
function [joinadata, Intervals ] = joinVariableData(conn, adata, bruto, idProduct, idQuality)

fn = fieldnames(adata);
Intervals = {} ; 
% First I look for the first non-empty data table
i=1 ; j=1; 
while i <= length(fn) && height(adata.(fn{i})) == 0
   i = i + 1 ; 
end
joinadata = adata.(fn{i}) ; 
Variable = adata.(fn{i}).Properties.VariableNames{2} ; 
Intervals.(fn{j}) = getVariableInterval(conn, Variable, bruto, idProduct, idQuality) ; 
i = i + 1 ; j=j+1  ; 
% Then I skip the empty adata tables
while i <= length(fn)
  while i <= length(fn) && height(adata.(fn{i})) == 0
      i = i + 1 ; 
  end
  while i <= length(fn) && height(adata.(fn{i})) > 0
      joinadata = outerjoin(joinadata, adata.(fn{i}), 'MergeKeys',true) ; 
      Variable = adata.(fn{i}).Properties.VariableNames{2} ; 
      Intervals.(fn{j}) = getVariableInterval(conn,  Variable, bruto, idProduct, idQuality) ; 
      i = i + 1 ; 
      j = j + 1 ; 
  end
end

end


