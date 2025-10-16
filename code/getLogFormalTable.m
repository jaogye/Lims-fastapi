function [sampleTable0, sampleTable1] = getLogFormalTable(sample)

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end


sampleTable0 = FormalTable();
%vvalue2 = string(strtrim( sample.TechnicalGrade(1)) ); 

Grade = strtrim( string (sample.Grade(1) ) ); 
TechnicalGrade = strtrim( string(sample.TechnicalGrade(1)) ); 
Bruto = strtrim( string( sample.Bruto(1) )); 
Product = "<html>" + Grade + "_" + TechnicalGrade + "_" + Bruto + "</html>" ; 
%Product = "<html>NABS - 39%_FG_NaHSO<sub>3</sub></html>" ; 
append(sampleTable0, getEntry1("                Product : ", Product ) )  ; 

vvalue1 = string(strtrim( sample.Customer(1)) ); 
append(sampleTable0, getEntry1("                Customer : " , vvalue1 ) ) ;

sampleTable1 = FormalTable();
vvalue1 = string( sample.ordernumber_PVS(1) ) ; 
vvalue2 = string(strtrim( sample.ordernumber_client(1)) ) ; 
append(sampleTable1, getEntry2( "PVS Chemicals Ref : ", vvalue1, "Client Order : ", vvalue2 )) ; 

vvalue1 = string(strtrim( sample.TestDate(1)) ) ; 
vvalue1 = datetime(vvalue1 ) ; 
vvalue1.Format = 'dd/MM/yyyy' ; 
vvalue1 = string(vvalue1) ; 

vvalue2 = string(strtrim( sample.SampleDate(1)) ) ; 
vvalue2 = datetime(vvalue2 ) ; 
vvalue2.Format = 'dd/MM/yyyy' ; 
vvalue2 = string(vvalue2) ; 

append(sampleTable1, getEntry2(  "Sampling Date : ", vvalue2, "Test Date : ", vvalue1) )  ; 

vvalue1 = string(strtrim( sample.BatchNumber(1)) ) ; 
vvalue2 = string(strtrim( sample.ContainerNumber(1)) ); 
append(sampleTable1, getEntry2( "Batch Number : ", vvalue1, "Container Number : ", vvalue2 )) ; 

%Quantity :	blanc'	Technical Data sheet :	9.KL.RE.013
%vvalue1 = string(strtrim( sample.BatchNumber(1)) ) ; 
vvalue2 = string(strtrim( sample.TDS(1)) ); 
append(sampleTable1, getEntry2( "Quantity : ", "", "Technical Data sheet : ", vvalue2 )) ; 


%sampleTable = Table({sampleTable1,' ',sampleTable2});
%sampleTable.entry(1,1).Style = {Width('3.2in')};
%sampleTable.entry(1,2).Style = {Width('.2in')};
%sampleTable.entry(1,3).Style = {Width('3.2in')};
%sampleTable.Style = {Width('100%'), ResizeToFitContents(false)};

end

function row = getEntry1(field1, value1)

row = mlreportgen.dom.TableRow();
txt1 = mlreportgen.dom.Text(field1) ; 
txt1.WhiteSpace =  "preserve" ; 
e1 = mlreportgen.dom.TableEntry(txt1 ) ; 
e1.Style = {mlreportgen.dom.Bold mlreportgen.dom.HAlign('Right')}  ; 

append(row, e1);
te = mlreportgen.dom.TableEntry( ) ;
append(te, mlreportgen.dom.HTML( value1 ) ) ; 
append(row, te );

end 

function row = getEntry2(field1, value1, field2, value2)

row = mlreportgen.dom.TableRow();

txt1 = mlreportgen.dom.Text(field1) ; 
txt1.WhiteSpace =  "preserve" ; 
e1 = mlreportgen.dom.TableEntry(txt1 ) ; 
e1.Style = {mlreportgen.dom.Bold mlreportgen.dom.HAlign('Right')}  ; 
append(row, e1);
append(row, mlreportgen.dom.TableEntry( value1 ) );

txt2 = mlreportgen.dom.Text(field2) ; 
txt2.WhiteSpace =  "preserve" ; 
e2 = mlreportgen.dom.TableEntry(txt2 ) ; 
e2.Style = {mlreportgen.dom.Bold mlreportgen.dom.HAlign('Right')}  ; 
append(row, e2);
append(row, mlreportgen.dom.TableEntry( value2 ) );

end 
