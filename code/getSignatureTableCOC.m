function [signatureTable,  signaturefileAdmin] = getSignatureTableCOC( conn, userName )

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

%[path, path_admin, user_Name, admin_Name] = getPathSignature(conn, userName) ; 
[~, signatureDataAdmin, ~, ~] = getSignatureData(conn, userName) ; 

formatofImage='png'; 

signaturefileAdmin = [tempname,'.',formatofImage]; 
fid2 = fopen(signaturefileAdmin, 'w'); 
fwrite(fid2, signatureDataAdmin, '*uint8');
sign_admin = Image(signaturefileAdmin);
fclose(fid2) ; 

signatureTable = Table() ; 
tr = TableRow();

date_table = Table();

sdate = datetime( ) ; 
sdate.Format = 'dd/MM/yyyy' ; 
txtdate = Text( "Ghent  :        "+ string( sdate )) ; 
txtdate.WhiteSpace =  "preserve" ; 

tr21 = TableRow();
append(tr21, TableEntry( txtdate) );
tr21.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('bottom')};
append(date_table, tr21 ) ;  
tr22 = TableRow();
append(tr22, TableEntry( Image(which('ShortLine.png' ))  )  ) ; 
tr22.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('top'), HAlign('Left') };
append(date_table, tr22 ) ;  
tr23 = TableRow();
append(tr23, TableEntry( "Date") );
tr23.Children(1).Style = {Width('2in'), Height('0.2in'), VAlign('top'), HAlign('center')};
append(date_table, tr23 ) ;  

%append(tr,TableEntry("      "));
append(tr,TableEntry(date_table));
%append(tr, TableEntry(date_table) );

tr.Children(1).Style = {Width('1in'), Height('1in')};
%  tr.Children(2).Style = {Width('3in'), Height('1in'), VAlign('top')};
%  tr.Children(3).Style = {Width('2in'), Height('1in'), VAlign('bottom')};
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

% delete(signaturefile);

end 