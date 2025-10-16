function  COCReportGen(conn, sample, filename, userName)

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

d=Report(filename,'docx');

pageSizeObj = PageSize("11.69in","8.27in","portrait");
d.Layout.PageSize = pageSizeObj;
pageMarginsObj = PageMargins();
pageMarginsObj.Top = "0.5in";
pageMarginsObj.Bottom = "0.1in";
pageMarginsObj.Left = "0.98in";
pageMarginsObj.Right = "0.98in";
pageMarginsObj.Header = "0in";
pageMarginsObj.Footer = "0in";
d.Layout.PageMargins = pageMarginsObj;

header=Image(which('cocheader.png'));
header.Style = [header.Style {ScaleToFit}];
append(d, header);

% Generation of Sample Header
hr3 = HorizontalRule();
hr3.BorderColor = 'black';
hr3.Border = 'solid';

[sampleTable0, sampleTable1] = getLogFormalTable(sample) ; 
append(d, sampleTable0 );
append(d, sampleTable1 );
append(d, hr3) ; 

txt = Text( "We hereby certify/declare that the quality of the above mentioned product complies with the latest version of the Technical Data sheet." )  ; 
txt.Style = {HAlign('center')} ; 

append(d, txt) ; 
append(d, hr3) ; 
[signatureTable, signaturefileAdmin] = getSignatureTableCOC( conn, userName) ; 
append(d,signatureTable) ; 

% Adding blank lines 
nn = 8 ; 
for i=1:nn
   append(d,"") ; 
end 

footer=Image(which('coafooter.png'));
footer.Style = [footer.Style {ScaleToFit}];
append(d,footer) ; 

close(d) ;
rptview(d);

delete(signaturefileAdmin);
end
