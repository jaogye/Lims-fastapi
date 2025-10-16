function  CertificateDayReportGen(conn, sample, measurement,filename, userName)

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

d=Report(filename,'pdf');

pageSizeObj = PageSize("11.69in","8.27in","portrait");
d.Layout.PageSize = pageSizeObj;
pageMarginsObj = PageMargins();
pageMarginsObj.Top = "0.5in";
pageMarginsObj.Bottom = "0.1in";
pageMarginsObj.Left = "0.01in";
pageMarginsObj.Right = "0.01in";
pageMarginsObj.Header = "0in";
pageMarginsObj.Footer = "0in";
d.Layout.PageMargins = pageMarginsObj;

header=Image(which('cdayheader.png'));
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

idx = matches( measurement.Test, 'Assay' ) ; 
index = find(idx) ; 

%measurementHeader = {'Test',  'Test Results', 'Specification', 'Unit'};
%measurementBody = table2cell(tt);
%measurementTable = FormalTable(measurementHeader, measurementBody);
%measurementTable.Header.Style = [measurementTable.Header.Style {Bold}];
%dataTableStyle = {Border('solid'), ColSep('solid'), RowSep('solid'), Width('100%'), OuterMargin('0pt', '0pt', '0pt', '0pt')};
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

i=1; 
    r = TableRow;
    r.Style = [r.Style bodyStyle];

    p = Paragraph(string( measurement.Test(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));
    
    p = Paragraph(string(measurement.Element(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));

    p = Paragraph(char(8804) + string(measurement.TestResults(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));

    if strcmp(measurement.Min(i), "")
       ss = "" ; 
    else 
       nn =str2double(measurement.Min(i)) ; 
       ss = num2str( nn,"%.3f") ;    
       if floor(100*nn) == 100*nn
          ss = num2str( nn,"%.2f") ;    
       end          
       if floor(nn) == nn
          ss = num2str( nn,"%.0f") ;    
       end   
    end
    p = Paragraph( ss ) ; 
    p.Style = [p.Style  {HAlign('center')}];
    append(r, TableEntry(p));

    if strcmp(measurement.Max(i), "")
       ss = "" ; 
    else 
       nn =str2double(measurement.Max(i)) ; 
       ss = num2str( nn,"%.3f") ;    
       if floor(100*nn) == 100*nn
          ss = num2str( nn,"%.2f") ;    
       end   
       if floor(nn) == nn
          ss = num2str( nn,"%.0f") ;    
       end   
       
    end
    p = Paragraph( ss );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));

    p = Paragraph(string(measurement.unit(i)) );
    p.Style = [p.Style  {HAlign('center')}];
    append(r,  TableEntry(p));    
    
    append(t, r);
append(d, t);


append(d, hr3) ; 
[signatureTable, sign_table3, signaturefile, signaturefileAdmin] = getSignatureTable( conn, userName) ; 
append(d,signatureTable) ; 
append(d, sign_table3 ) ; 

% Adding blank lines 
nn = 9 ; 
for i=1:nn
   append(d,"") ; 
end 

footer=Image(which('coafooter.png'));
footer.Style = [footer.Style {ScaleToFit}];
append(d,footer) ; 

close(d);
rptview(d);

delete(signaturefile);
delete(signaturefileAdmin);
end

