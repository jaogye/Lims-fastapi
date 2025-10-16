function InputData=readxls() 

    [InputFileName,InputPathName]=uigetfile('*.xlsx');
    filename=fullfile(InputPathName,'\',InputFileName);
    opts = detectImportOptions(filename);

    opts.VariableTypes=repmat("string",size(opts.VariableTypes));

    opts = setvaropts(opts, opts.VariableNames, "EmptyFieldRule", "auto");
    InputData=readtable(filename,opts);

end