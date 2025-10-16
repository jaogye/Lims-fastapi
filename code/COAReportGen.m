function COAReportGen(conn, sample, measurement,filename, userName)

if isdeployed==1
    makeDOMCompilable();
end
 import mlreportgen.report.*
import mlreportgen.dom.*

d=Report(filename,'pdf');

pageSizeObj = PageSize("11.69in","8.27in","portrait");
d.Layout.PageSize = pageSizeObj;
pageMarginsObj = PageMargins();
pageMarginsObj.Top = "0.5in";
pageMarginsObj.Bottom = "0.2in";
%pageMarginsObj.Left = "0.98in";
pageMarginsObj.Left = "0.1in";
%pageMarginsObj.Right = "0.98in";
pageMarginsObj.Right = "0.1in";
pageMarginsObj.Header = "0in";
pageMarginsObj.Footer = "0in";
d.Layout.PageMargins = pageMarginsObj;

header=Image(which('coaheader.png'));
header.Style = [header.Style {ScaleToFit}];
append(d, header);

% Generation of Sample Header
hr3 = HorizontalRule();
hr3.BorderColor = 'black';
hr3.Border = 'solid';

[sampleTable0, sampleTable1] = getCOAFormalTable(sample) ; 
append(d, sampleTable0 );
append(d, sampleTable1 );
append(d, hr3) ; 

% Generation of Test Results 
%measurementHeader = {'Test', 'Element', 'Test Results', 'Specification', 'Unit'};
%measurementBody = table2cell(measurement);

%measurementTable = FormalTable(measurementHeader, measurementBody);
%measurementTable.Header.Style = [measurementTable.Header.Style {Bold}];
%%dataTableStyle = {Border('solid'), ColSep('solid'), RowSep('solid'), Width('100%'), OuterMargin('0pt', '0pt', '0pt', '0pt')};
%dataTableStyle = {  Width('100%'), OuterMargin('0pt', '0pt', '0pt', '0pt')};
%measurementTable.Style = [measurementTable.Style dataTableStyle];
%append(d, measurementTable);

tableStyle = {Width('100%')};
mainHeaderRowStyle = {VAlign('middle'), InnerMargin('2pt', '2pt', '2pt', '2pt')};
mainHeaderTextStyle = {Bold, OuterMargin('0pt', '0pt', '0pt', '0pt'), FontFamily('Arial')};
bodyStyle = {OuterMargin('0pt', '0pt', '0pt', '0pt'), InnerMargin('2pt', '2pt', '2pt', '0pt')};

t = Table(6);
t.Style = [t.Style tableStyle];

r = TableRow;
r.Style = [r.Style mainHeaderRowStyle];

p = Paragraph('Test');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r, TableEntry(p));
p = Paragraph('Element');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r, TableEntry(p));
p = Paragraph('Test Results');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r, TableEntry(p));
p = Paragraph('Specification');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
te = TableEntry(p);
te.ColSpan = 2;
append(r, te);
p = Paragraph('Unit');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r, TableEntry(p));
append(t, r);

r = TableRow;
append(r, TableEntry(Paragraph("")) );
append(r, TableEntry(Paragraph("")) );
append(r, TableEntry(Paragraph("")) );
p = Paragraph('Min');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r,  TableEntry(p));
p = Paragraph('Max');
p.Style = [p.Style mainHeaderTextStyle {HAlign('center')}];
append(r, TableEntry(p));
append(r, TableEntry(Paragraph('')) );
append(t, r);

for i = 1:height(measurement)
    r = TableRow;
    r.Style = [r.Style bodyStyle];

    p = Paragraph(string( measurement.Test(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));
    
    p = Paragraph(string(measurement.Element(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));

    value = measurement.TestResults(i) ; 
    str_value = string(value) ; 
    % If the value has 1 decimal of precision
    if value - floor(value) > 0 && 10*value - floor(10*value) == 0
       str_value = sprintf('%0.1f', value) ; 
    end     
    if value - floor(value) == 0 && measurement.typevar(i) == "I"
       if string(measurement.unit(i)) == "kg/m³"
       else
          if strcmp( sample.onedecimal(1), "Y" )
             str_value = sprintf('%0.1f', value) ;  
          end
       end    
    end     
    %p = Paragraph(char(8804) + string(measurement.TestResults(i)) );
    if measurement.typevar(i) == "I"
       if measurement.less(i)
          %p = Paragraph( char(8804) + string(measurement.TestResults(i)) );
          p = Paragraph( "<" + str_value );
       else 
          p = Paragraph( str_value );        
       end
    else
      p = Paragraph( string(measurement.listvalue(i)) );         
    end
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));   

    mm = strtrim(measurement.Min(i)) ; 
    if strcmp( mm, "NULL" ) || strcmp( mm, "0" )
       ss = "" ; 
    else
       ss = strtrim( string(measurement.Min(i)) );  
    end 

    p = Paragraph( ss ) ; 
    p.Style = [p.Style  {HAlign('center')}];
    append(r, TableEntry(p));

    mm = strtrim(measurement.Max(i)) ; 
    if strcmp( mm, "NULL" ) || strcmp( mm, "0" )
       ss = "" ; 
    else
       ss = strtrim( string(measurement.Max(i)) );  
    end 
       
    p = Paragraph( ss );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));

    p = Paragraph(string(measurement.unit(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));    
    
    append(t, r);
end
append(d, t);


append(d, hr3) ; 
[signatureTable, sign_table3, signaturefile, signaturefileAdmin] = getSignatureTable( conn, userName) ; 

append(d,signatureTable) ; 
append(d, sign_table3 ) ; 

% Adding blank lines 
nn = floor(8 - 2*height(measurement)/3 ) ; 
%nn=2 ; % h = 9
%nn=6 ; % h = 3
for i=1:nn
   append(d,"") ; 
end 

footer=Image(which('coafooter.png'));
footer.Style = [footer.Style {ScaleToFit}];
append(d,footer) ; 

close(d); 

rptview(d);

%delete(signaturefile);
%delete(signaturefileAdmin);

end 
