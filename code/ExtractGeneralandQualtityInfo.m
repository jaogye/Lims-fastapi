function [GeneralInfoTable,SpecifictionTable] = ExtractGeneralandQualtityInfo(app)
%% Extracts General Information and Spec table for Logistics, day, dayloading etc...
%
%
%%
AugmentedLogisticData=app.config.AugmentedLogisticData;
AugmentedDayData=app.config.AugmentedDayData;
AugmentedDayLoadingData=app.config.AugmentedDayLoadingData;
%% create sample number array
% for Logistic
numstring=arrayfun(@(x)sprintf('%03d',x),(1:1:height(AugmentedLogisticData))','UniformOutput',false);
SampleNumber=join([repmat("S",height(AugmentedLogisticData),1) ...
    repmat(datestr(now,'ddmmyyyy'),height(AugmentedLogisticData),1)...
    numstring, AugmentedLogisticData.certificaat],'_');
SampleNumber=replace(SampleNumber,'_Y','_LC');
SampleNumber=replace(SampleNumber,'_N','_L');
% for day data
indexA=height(AugmentedLogisticData)+1;
indexB=height(AugmentedLogisticData)+height(AugmentedDayData);
numstring=arrayfun(@(x)sprintf('%03d',x),(indexA:1:indexB)','UniformOutput',false);
SampleNumber=[SampleNumber;join([repmat("S",height(AugmentedDayData),1) ...
    repmat(datestr(now,'ddmmyyyy'),height(AugmentedDayData),1)...
    numstring,repmat("P",height(AugmentedDayData),1)],'_')];

% for day loading
indexA=indexB+1;
indexB=indexA+height(AugmentedDayLoadingData)-1;
numstring=arrayfun(@(x)sprintf('%03d',x),(indexA:1:indexB)','UniformOutput',false);

SampleNumber=[SampleNumber;join([repmat("S",height(AugmentedDayLoadingData),1) ...
    repmat(datestr(now,'ddmmyyyy'),height(AugmentedDayLoadingData),1)...
    numstring,repmat("PL",height(AugmentedDayLoadingData),1)],'_')];


%%
%% create General information Table 

ClientName=[AugmentedLogisticData.Klant;AugmentedDayData.Klant;AugmentedDayLoadingData.Klant];
ArticleCode=[AugmentedLogisticData.article_no;AugmentedDayData.article_no;AugmentedDayLoadingData.article_no];
Product=[AugmentedLogisticData.Product;AugmentedDayData.Product;AugmentedDayLoadingData.Product];
Quality=[AugmentedLogisticData.Quality;AugmentedDayData.Quality;AugmentedDayLoadingData.Quality];
Tank=[AugmentedLogisticData.SamplePoint;AugmentedDayData.SamplePoint;AugmentedDayLoadingData.SamplePoint];
SampleDate=[AugmentedLogisticData.date;repmat(datestr(now),height(AugmentedDayData),1);repmat(datestr(now),height(AugmentedDayLoadingData),1)];
TestDate=[AugmentedLogisticData.date;repmat(datestr(now),height(AugmentedDayData),1);repmat(datestr(now),height(AugmentedDayLoadingData),1)];

GeneralInfoTable=table(SampleNumber,ClientName,ArticleCode,Product,Quality,Tank,SampleDate,TestDate);
%% create Spec table
% get spec spect table for augmented logistic data
SpecTable=AugmentedLogisticData(:,find(matches(AugmentedLogisticData.Properties.VariableNames,'conc')):end);
SpecNames=SpecTable.Properties.VariableNames';
ProductInfo=AugmentedLogisticData.Product;
QualityInfo=AugmentedLogisticData.Quality;


GeneralSpec=app.config.data.spec;
SpecTable_L=arrayfun(@(x)ExctractSpecification(SpecTable,SpecNames,GeneralSpec,ProductInfo,QualityInfo,x),1:1:height(SpecTable));

% get spec table for day Data

SpecTable=AugmentedDayData(:,find(matches(AugmentedDayData.Properties.VariableNames,'conc')):end-2);
SpecNames=SpecTable.Properties.VariableNames';
ProductInfo=AugmentedDayData.Product;
QualityInfo=AugmentedDayData.Quality;
SpecTable_day=arrayfun(@(x)ExctractSpecification(SpecTable,SpecNames,GeneralSpec,ProductInfo,QualityInfo,x),1:1:height(SpecTable));

% get spec table for day loading

SpecTable=AugmentedDayLoadingData(:,find(matches(AugmentedDayLoadingData.Properties.VariableNames,'conc')):end-2);
SpecNames=SpecTable.Properties.VariableNames';
ProductInfo=AugmentedDayLoadingData.Product;
QualityInfo=AugmentedDayLoadingData.Quality;
SpecTable_dayL=arrayfun(@(x)ExctractSpecification(SpecTable,SpecNames,GeneralSpec,ProductInfo,QualityInfo,x),1:1:height(SpecTable));

% combined spec table

SpecTable=[SpecTable_L,SpecTable_day,SpecTable_dayL]';

% create final spec table for Lab technical person to update
SpecifictionTable=table(SampleNumber,SpecTable);

end