function [signatureTable, sign_table3, signaturefile, signaturefileAdmin] = getSignatureTable( conn, userName )

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

signaturefile = '' ;  signaturefileAdmin='' ; 
[signatureData, signatureDataAdmin, ~, ~] = getSignatureData(conn, userName) ; 

formatofImage='png'; 
%if isempty( signatureData ) 
%   sign = []; 
%else 
  signaturefile=[userName,'.',formatofImage];    
  sign = Image(which(signaturefile));
%end     

%if isempty( signatureDataAdmin ) 
%   sign_admin = []; 
%else   
   signaturefilAdmin=['adminSignature' ,'.',formatofImage];
   sign_admin = Image(which(signaturefilAdmin));   
%end


signatureTable = Table() ; 
tr = TableRow();

tr11 = TableRow();
txt11 = Text( "Lab test conducted and verified by" ) ; 
append(tr11, TableEntry( txt11) );
tr11.Children(1).Style = {Width('3in'), Height('0.2in'), VAlign('top'), HAlign('center')};

tr12 = TableRow();
append(tr12,TableEntry(sign) );
tr12.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('bottom')};

%tr13 = TableRow();
%te = TableEntry( Image(which('ShortLine.png' ))  ) ; 
%te.ColSpan = 2;
%append(tr13,te);
%tr13.Children(1).Style = {Width('2in'), Height('0.08in'), VAlign('top')};

%tr14 = TableRow();
%txt14 = Text( "Lab Tester") ; 
%append(tr14, TableEntry( txt14) );
%tr14.Children(1).Style = {Width('2in'), Height('0.08in'), VAlign('top'), HAlign('center')};

sign_table = Table();
append(sign_table, tr11);
append(sign_table, tr12);
%append(sign_table, tr13);
%append(sign_table, tr14);
append(tr,TableEntry(sign_table));
append(tr,TableEntry("      "));

date_table = Table();

sdate = datetime( ) ; 
sdate.Format = 'dd/MM/yyyy' ; 
txtdate = Text( string(repmat(' ' ,[1 37])) + "Ghent   :    "+ string( sdate )) ; 
txtdate.WhiteSpace =  "preserve" ; 

tr21 = TableRow();
append(tr21, TableEntry( txtdate) );
tr21.Children(1).Style = {Width('3.5in'), Height('0.2in'), VAlign('bottom')};
append(date_table, tr21 ) ;  
tr22 = TableRow();
append(tr22, TableEntry( Image(which('ShortLine.png' ))  )  ) ; 
tr22.Children(1).Style = {Width('3in'), Height('0.2in'), VAlign('top'), HAlign('Left') };
append(date_table, tr22 ) ;  
tr23 = TableRow();

txtdate2 = Text( string(repmat(' ' ,[1 30])) +"Date" ) ; 
txtdate2.WhiteSpace =  "preserve" ; 

append(tr23, TableEntry( txtdate2) );
tr23.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('top'), HAlign('center')};
append(date_table, tr23 ) ;  

append(tr, TableEntry(date_table) );

tr.Children(1).Style = {Width('1in'), Height('1in')};
tr.Children(2).Style = {Width('3in'), Height('1in')};
tr.Children(3).Style = {Width('2in'), Height('1in'), VAlign('bottom')};
tr.Style = {Width('100%'), ResizeToFitContents(false)};
append( signatureTable, tr) ; 

% --------------------------------------

tr31 = TableRow();
txt31 = Text( "Lab test approved by" ) ; 
append(tr31, TableEntry( txt31 ));
tr31.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('top'), HAlign('center')};

tr32 = TableRow();
append(tr32,TableEntry(sign_admin) );
tr32.Children(1).Style = {Width('2in'), Height('0.3in'), VAlign('bottom')};

%tr33 = TableRow();
%te = TableEntry( Image(which('ShortLine.png' ))  ) ; 
%te.ColSpan = 2;
%append(tr33, TableEntry( Image(which('ShortLine.png' ))  )  );
%tr33.Children(1).Style = {Width('2in'), Height('0.08in'), VAlign('top')};

%tr34 = TableRow();
%txt34 = Text( "Quality Supervisor") ; 
%append(tr34, TableEntry( txt34) );
%tr34.Children(1).Style = {Width('2in'), Height('0.08in'), VAlign('top'), HAlign('center')};

sign_table3 = Table();
append(sign_table3, tr31);
append(sign_table3, tr32);
%append(sign_table3, tr33);
%append(sign_table3, tr34);



end 