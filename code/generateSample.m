% This function generates the samples for each day in a range of dates
function generateSample(conn, iduser)
% Define start and end dates
startDate = datetime('2023-11-13');
endDate = datetime('2024-03-31');

% Generate a sequence of dates
dateSequence = startDate:endDate;

% Convert the date sequence to a cell array of strings
dateArray = cellstr(datestr(dateSequence, 'yyyy-mm-dd'));

for i= 1:length(dateArray)
    disp(dateArray{i})
   [msgerror, pendingdata] = loadCustomerSample(conn, dateArray{i}, iduser) ;
   msgerror1 = loadProductionSample(conn, dateArray{i}, iduser) ;
end

