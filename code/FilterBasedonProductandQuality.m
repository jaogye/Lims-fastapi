function [dataOut] = FilterBasedonProductandQuality(tempdata,productinfo)
%% This function filters the client table 
% Based on product info  table ( article, product and quality)
%
% Input = client table and product info
% Output= Filterd table
%%


% filter based on quality

z=contains(tempdata.Quality,productinfo.Quality);

% filter based on Product

y=contains(tempdata.Product,productinfo.Product);

dataOut=tempdata(y&z,:);

% dataOut =[] then product only filter
if(isempty(dataOut))
    dataOut=tempdata(y,:);
end

% case a data out unique but quality info missing
% case b data out again empty because of round off in concentration
% case c data out is not empty but not unique
 sizeofdataOut=height(dataOut);
%
switch sizeofdataOut

    case 1
        % unique but quality info missing (case a)
        if(matches(dataOut.Quality,""))
            dataOut.Quality=productinfo.Quality; 
        end
    case 0
        % case b
          % first filter quality 
              dataOut=tempdata(z,:);
            
              pat="%"|"-";
              productname_split=split(productinfo.Product,pat);
              % filter based on product name
              tempdataOut=dataOut(contains(dataOut.Product,productname_split(1)),:);
              % gget concentration as a rounded number
              concen=str2double(productname_split(2));
              concen=string(round(concen*0.1));
              tempdataOut=tempdataOut(contains(tempdataOut.Product,concen),:);
              dataOut=tempdataOut;

    otherwise
        % not unique so filter based on certificate case c
        dataOut=dataOut(contains(dataOut.Quality,"")&contains(dataOut.certificaat,'Y'),:);
        if(~isempty(dataOut))
            dataOut=dataOut(1,:);
            dataOut.Quality=productinfo.Quality;
       
        end

end
end