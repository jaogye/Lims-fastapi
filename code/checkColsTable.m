function [ok, msg] = checkColsTable(conn, data, stable)

cols = varColumns(conn, stable ) ; 

%cols = { "Action" , "Customer", "Product" , "Quality" ,'Status', "Certificaat" , "Opm", "Day_COA",    "COC", "Visual", "conc" , ...
%"Free_SO3", "Free_HCl",    "pH",    "NH3",    "ATS", "densiteit", "NTU", "Particulate_matter",  "kleur", "SO3", "SO2", "Cl", "Nox", "PO4", ...
%"Kristallisatie", "Residu", "Fe", "Cr" ,"Ni", "As", "Ba", "Ca",  "Na", "Al", "Cd",    "Cu",  "K", "Mg", "Pb" ,"Hg", "Zn", "Sb", ...
%"V", "Se", "Li" , "Be", "B", "In",  "Sn", "Ta",  "Au" , "Tl", "Bi" , "Ti" , "Mn" , "Co" , "Ga" ,"Sr" , "Zr" , "Nb" , "Mo"  , "Ge",  "id" } ; 

ok = 1 ; 
msg = "" ; 
for i=1:length(cols)
    if not ( strcmp( cols{1,i}, data.Properties.VariableNames{i} ) )
       msg = "Incorrect order of columns. Expected column: " + cols{1,i} + " but it is received :" + data.Properties.VariableNames{i} ; 
       ok = 0 ;
       return 
    end
end

end
