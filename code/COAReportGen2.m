function COAReportGen2(app, conn, sample, measurement,filename, userName)

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

app.Console.Value = [app.Console.Value ;  "step1"] ; 
d=Report(filename,'pdf');
app.Console.Value = [app.Console.Value ;  "step2"]   ; 

pageSizeObj = PageSize("11.69in","8.27in","portrait");
app.Console.Value = [app.Console.Value ;  "step3"] ; 

d.Layout.PageSize = pageSizeObj;
app.Console.Value = [app.Console.Value ;  "step4"] ;

pageMarginsObj = PageMargins();
app.Console.Value = [app.Console.Value ;  "step5"] ;
pageMarginsObj.Top = "0.5in";
app.Console.Value = [app.Console.Value ;  "step6"] ;
pageMarginsObj.Bottom = "0.2in";
app.Console.Value = [app.Console.Value ;  "step7"] ;
pageMarginsObj.Left = "0.98in";
app.Console.Value = [app.Console.Value ;  "step8"] ;
pageMarginsObj.Right = "0.98in";
app.Console.Value = [app.Console.Value ;  "step9"] ;
pageMarginsObj.Header = "0in";
app.Console.Value = [app.Console.Value ;  "step10"] ;
pageMarginsObj.Footer = "0in";
app.Console.Value = [app.Console.Value ;  "step11"] ;
d.Layout.PageMargins = pageMarginsObj;
app.Console.Value = [app.Console.Value ;  "step12"] ;

header=Image(which('coaheader.png'));
app.Console.Value = [app.Console.Value ;  "step13"] ;
header.Style = [header.Style {ScaleToFit}];
app.Console.Value =  [app.Console.Value ;  "step14"] ;
append(d, header);

app.Console.Value = [app.Console.Value ;  "step15"] ;
% Generation of Sample Header
hr3 = HorizontalRule();
hr3.BorderColor = 'black';
hr3.Border = 'solid';

[sampleTable0, sampleTable1] = getSampleFormalTable(sample) ; 
append(d, sampleTable0 );
append(d, sampleTable1 );
append(d, hr3) ; 

% Generation of Test Results 
measurementHeader = {'Test', 'Element', 'Test Results', 'Specification', 'Unit'};
measurementBody = table2cell(measurement);

app.Console.Value = [app.Console.Value ;  "step16"] ;
measurementTable = FormalTable(measurementHeader, measurementBody);
measurementTable.Header.Style = [measurementTable.Header.Style {Bold}];
%dataTableStyle = {Border('solid'), ColSep('solid'), RowSep('solid'), Width('100%'), OuterMargin('0pt', '0pt', '0pt', '0pt')};

app.Console.Value = [app.Console.Value ;  "step17"] ;
dataTableStyle = {  Width('100%'), OuterMargin('0pt', '0pt', '0pt', '0pt')};

measurementTable.Style = [measurementTable.Style dataTableStyle];
append(d, measurementTable);

app.Console.Value = [app.Console.Value ;  "step18"] ;
append(d, hr3) ; 

close(d) ; 
app.Console.Value = [app.Console.Value ;  "step19"] ;
%rptview(d);
end

