function Qtable=ExctractSpecification(SpecTable,SpecNames,GeneralSpec,ProductInfo,QualityInfo,i)
%% Extract specification 
%
%
%%

%index=find(~matches(table2array(SpecTable(i,:)),"")); % remove blank spec and -9999
index=find(and(~matches(table2array(SpecTable(i,:)),""),~matches(table2array(SpecTable(i,:)),"-9999")));
Items=SpecNames(index);
specRange=(table2array(SpecTable(i,index)))';

% replace x value from spec table
if(~isempty(index))
for j =1:length(specRange)
    if(~matches(specRange(j),"x") )
    [Min(j,1),Value(j,1),Max(j,1)] = getSpecRange(specRange(j));
    else
        %disp(specRange(j))
        % get general spec from product and quality info
       GeneralSpecFiltered= GeneralSpec(matches(GeneralSpec.Product,ProductInfo(i)) & matches(GeneralSpec.Quality,QualityInfo(i)) ,:);
       % get specrange
       if(~isempty(GeneralSpecFiltered))
       genspec=table2array(GeneralSpecFiltered(1,matches(GeneralSpecFiltered.Properties.VariableNames,Items(j))));
       else
           genspec=" ";
       end
       if(isempty(genspec))
         [Min(j,1),Value(j,1),Max(j,1)] = getSpecRange(" ");  
       else
           [Min(j,1),Value(j,1),Max(j,1)] = getSpecRange(genspec);
       end
    end
end
% create output table
OOS=false(size(Value)); % out of spec condition, default to false
Qtable={table(Items,Min,Value,Max,OOS)};
else
Qtable={table()};
end


end

function [Min,Value,Max] = getSpecRange(input)

pat= '<'|"-"|">";
if(isempty(input))
% initialize to empty
Min=string.empty;
Max=string.empty;
Value=string.empty;
end

    % extract symbol <  > - x

    sign=extract(input,pat);

    range=extract(input,digitsPattern);

    switch sign

        case "-"
            Min=range(1);
            Max=range(2);
            Value="";
        case "<"
            Min="";
            Max=range(1);
            Value="";

        case ">"
            Min="";
            Max=range(1);
            Value="";
        otherwise
            Min="";
            Max="";
            Value="";
    end


end

