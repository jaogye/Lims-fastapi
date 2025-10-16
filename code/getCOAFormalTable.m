function [sampleTable0, sampleTable1] = getCOAFormalTable(sample)

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

% sampleHeader = {'Grade', 'TechnicalGrade', 'Customer', 'Order PVS', 'Order Client', 'Sample Date', 'Test Date', 'Batch Number', 'Container Number'};

sampleTable0 = FormalTable();
%vvalue2 = string(strtrim( sample.TechnicalGrade(1)) ); 

Grade = strtrim( string (sample.Grade(1) ) ); 
TechnicalGrade = strtrim( string(sample.TechnicalGrade(1)) ); 
Bruto = strtrim( string( sample.Bruto(1) )); 
Product = "<html>" + Grade + "_" + TechnicalGrade + "_" + Bruto + "</html>" ; 
%Product = "<html>NABS - 39%_FG_NaHSO<sub>3</sub></html>" ; 
append(sampleTable0, getEntry1( repmat(' ',[1 30]) + "Product  : ", Product ) )  ; 

vvalue1 = string(strtrim( sample.Customer(1)) ); 
vvalue1 = strrep(vvalue1,'&','&amp;') ; 
append(sampleTable0, getEntry1(repmat(' ',[1 30]) + "Customer  : " , vvalue1 ) ) ;

sampleTable1 = FormalTable();
vvalue1 = strtrim( string( sample.ordernumber_PVS(1) )) ; 
vvalue2 = strtrim( string( sample.ordernumber_client(1)) ) ; 
append(sampleTable1, getEntry2( "PVS Chemicals Ref  : ", vvalue1, "Customer Ref  : ", vvalue2 )) ; 

vvalue1 = string(strtrim( sample.TestDate(1)) ) ; 
vvalue1 = datetime(vvalue1 ) ; 
vvalue1.Format = 'dd/MM/yyyy' ; 
vvalue1 = string(vvalue1) ; 
if ismissing(vvalue1)
   vvalue1 =  "No test date"; 
end    

vvalue2 = string(strtrim( sample.SampleDate(1)) ) ; 
vvalue2 = datetime(vvalue2 ) ; 
vvalue2.Format = 'dd/MM/yyyy' ; 
vvalue2 = string(vvalue2) ; 

append(sampleTable1, getEntry2( repmat(' ',[1 20]) + "Sampling Date  : ", vvalue2, repmat(' ',[1 55]) +  "Test Date  : ", vvalue1) )  ; 

vvalue1 = string(strtrim( sample.BatchNumber(1)) ) ; 
vvalue2 = string(strtrim( sample.ContainerNumber(1)) ); 

if not( strcmp(vvalue1,"") ) || not( strcmp(vvalue2,"") )
   append(sampleTable1, getEntry2( "Batch Number  : ", vvalue1, "  Container  : ", vvalue2 )) ; 
end 
%sampleTable = Table({sampleTable1,' ',sampleTable2});
%sampleTable.entry(1,1).Style = {Width('3.2in')};
%sampleTable.entry(1,2).Style = {Width('.2in')};
%sampleTable.entry(1,3).Style = {Width('3.2in')};
%sampleTable.Style = {Width('100%'), ResizeToFitContents(false)};

end

% function to create a row with one value
function row = getEntry1(field1, value1)

row = mlreportgen.dom.TableRow();
txt1 = mlreportgen.dom.Text(field1) ; 
txt1.WhiteSpace =  "preserve" ; 
e1 = mlreportgen.dom.TableEntry(txt1 ) ; 
e1.Style = {mlreportgen.dom.Bold mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Right')}  ; 
append(row, e1);

te = mlreportgen.dom.TableEntry( ) ;
te.Style = {mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Left') mlreportgen.dom.VAlign('middle') }  ;
append(te, mlreportgen.dom.HTML( value1 ) ) ; 
append(row, te );

end 

% function to create a row with two values
function row = getEntry2(field1, value1, field2, value2)

row = mlreportgen.dom.TableRow();
txt1 = mlreportgen.dom.Text(field1) ; 
txt1.WhiteSpace =  "preserve" ; 
e1 = mlreportgen.dom.TableEntry(txt1 ) ; 
e1.Style = {mlreportgen.dom.Bold mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Right')}  ; 
append(row, e1);

txt1v = mlreportgen.dom.Text(value1) ; 
te1 = mlreportgen.dom.TableEntry( txt1v ) ;
te1.Style = {mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Left') mlreportgen.dom.VAlign('Middle')}  ;
append(row, te1 );
%append(row, mlreportgen.dom.TableEntry( value1 ) );

txt2 = mlreportgen.dom.Text(field2) ; 
txt2.WhiteSpace =  "preserve" ; 
e2 = mlreportgen.dom.TableEntry(txt2 ) ; 
e2.Style = {mlreportgen.dom.Bold mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Right') }  ; 
append(row, e2);

txt2v = mlreportgen.dom.Text(value2) ; 
te2 = mlreportgen.dom.TableEntry( txt2v ) ;
te2.Style = {mlreportgen.dom.FontSize('12') mlreportgen.dom.HAlign('Left') mlreportgen.dom.VAlign('Middle') }  ;
append(row, te2 );

%append(row, mlreportgen.dom.TableEntry( value2 ) );

end 
