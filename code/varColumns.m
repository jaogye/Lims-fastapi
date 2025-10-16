% This function extracts the column's name of input excel sheets  
function Cols = varColumns(conn, table)
vars = select( conn, "SELECT shortname name, typevar  FROM variable ORDER BY ord" ) ; 
Cols = {} ; 
switch table

    case 'db.spec'
       Cols{length(Cols)+1} = "' ' Action" ; 
       Cols{length(Cols)+1} = "s.TDS" ; 
       Cols{length(Cols)+1} = "p.name Product" ; 
       Cols{length(Cols)+1} = "q.name Quality" ; 
       Cols{length(Cols)+1} = "s.Visual" ; 
       Cols{length(Cols)+1} = "v1.shortname Variable1" ; 
       Cols{length(Cols)+1} = "v2.shortname Variable2" ; 
       Cols{length(Cols)+1} = "v3.shortname Variable3" ;        

       for i = 1:height(vars)
           if vars.typevar(i) == "I"
              Cols{length(Cols)+1} = "min_" + strtrim( string( vars.name(i)) );          
              Cols{length(Cols)+1} = "max_" + strtrim( string( vars.name(i)) );          
           else    
              Cols{length(Cols)+1} = strtrim( string( vars.name(i)) );           
           end 
       end       
       Cols{length(Cols)+1} = "s.id" ; 
       
    case 'tbl.spec'
        Cols{length(Cols)+1} = "Action"; 
        Cols{length(Cols)+1} = "TDS"; 
        Cols{length(Cols)+1} = "Product"; 
        Cols{length(Cols)+1} = "Quality";  
        Cols{length(Cols)+1} = "Visual";
        Cols{length(Cols)+1} = "Variable1";        
        Cols{length(Cols)+1} = "Variable2";        
        Cols{length(Cols)+1} = "Variable3";                
       
    case 'db.customerlist'   
       Cols{length(Cols)+1} = "' ' Action" ; 
       Cols{length(Cols)+1} = "s.Customer" ; 
       Cols{length(Cols)+1} = "p.name Product" ; 
       Cols{length(Cols)+1} = "q.name Quality" ; 
       Cols{length(Cols)+1} = "s.Status" ; 
       Cols{length(Cols)+1} = "s.Certificaat" ; 
       Cols{length(Cols)+1} = "s.Opm" ; 
       Cols{length(Cols)+1} = "s.COA" ;        
       Cols{length(Cols)+1} = "s.Day_COA" ; 
       Cols{length(Cols)+1} = "s.COC" ; 
       Cols{length(Cols)+1} = "s.Visual" ; 
       Cols{length(Cols)+1} = "s.OneDecimal" ;        
       for i = 1:height(vars)
           if vars.typevar(i) == "I"
              Cols{length(Cols)+1} = "min_" + strtrim( string( vars.name(i)) );          
              Cols{length(Cols)+1} = "max_" + strtrim( string( vars.name(i)) );          
           else    
              Cols{length(Cols)+1} = strtrim( string( vars.name(i)) );           
           end 
       end       
       Cols{length(Cols)+1} = "s.id" ; 

    case 'tbl.customerlist'
        Cols{length(Cols)+1} = "Action" ; 
        Cols{length(Cols)+1} = "Customer";
        Cols{length(Cols)+1} = "Product" ; 
        Cols{length(Cols)+1} = "Quality" ;
        Cols{length(Cols)+1} = "Status";                 
        Cols{length(Cols)+1} = "Certificaat" ; 
        Cols{length(Cols)+1} = "Opm"; 
        Cols{length(Cols)+1} = "COA";            
        Cols{length(Cols)+1} = "Day_COA";    
        Cols{length(Cols)+1} = "COC"; 
        Cols{length(Cols)+1} = "Visual";
        Cols{length(Cols)+1} = "OneDecimal";
       
    case 'db.samplematrix'
       Cols{length(Cols)+1} = "' ' Action" ; 
       Cols{length(Cols)+1} = "p.name Product" ; 
       Cols{length(Cols)+1} = "q.name Quality" ; 
       Cols{length(Cols)+1} = "sp.name SamplePoint" ; 
       Cols{length(Cols)+1} = "s.Frequency" ; 
       Cols{length(Cols)+1} = "iif(s.has_visual=1, 'X', ' ')  Visual" ; 
       for i = 1:height(vars)
           Cols{length(Cols)+1} = "has_" + strtrim( string( vars.name(i)) ); 
       end             
       Cols{length(Cols)+1} = "s.id" ; 

    case 'tbl.samplematrix'
        Cols{length(Cols)+1} = "Action" ; 
        Cols{length(Cols)+1} = "Product" ; 
        Cols{length(Cols)+1} = "Quality" ; 
        Cols{length(Cols)+1} = "SamplePoint"; 
        Cols{length(Cols)+1} = "Frequency"; 
        Cols{length(Cols)+1} = "Visual";
end

if strcmp(extractBetween( table,1,3), "tbl")
   for i = 1:height(vars)
        Cols{length(Cols)+1} = strtrim( string( vars.name(i)) );           
    end       
    Cols{length(Cols)+1} = "id";
end

end