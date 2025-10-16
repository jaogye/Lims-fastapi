function reporttmp()

%import mlreportgen.dom.*;
%import mlreportgen.report.*;

import mlreportgen.report.*
import mlreportgen.dom.*
rpt = Document('myReport','pdf');
h = uitable('Data', [1 2; 3 4], 'ColumnName', {'HOLA', '<html>NABS - 39%_FG_NaHSO<sub>3</sub></html>'}) ; 
% Create table header row containing HTML content
tblHeaderRow = TableRow();
for i = 1:length(h.ColumnName)
    te = TableEntry();
    append(te,HTML(h.ColumnName{i})); % append content using DOM HTML object
    append(tblHeaderRow,te);
end
bodyContent=h.Data ; 
tbl = FormalTable(bodyContent); % create table with just body content
append(tbl.Header,tblHeaderRow); % append the header row
tbl.Border = 'solid';
tbl.ColSep = 'solid';
tbl.RowSep = 'solid';
append(rpt,tbl);
close(rpt) ;
rptview(rpt);

end 