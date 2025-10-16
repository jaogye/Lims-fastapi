function resp = module_LoL(str_function, cell_args)
    if     strcmp(str_function,'myfun_1')
        resp = myfun_1(cell_args);
        
    elseif strcmp(str_function,'myfun_2')
        resp = myfun_2(cell_args);
        
    elseif strcmp(str_function,'myfun_3')
        resp = myfun_3(cell_args);
        
    end %endif str_function
end %endmod module_LoL
% functions inside module -------------------
function resp = myfun_1(cell_args)
    % arithmetic mean
    [input_1, input_2] = cell_args{:};
    
    resp    = (input_1 + input_2)/2;
end % endfun myfun_1
function resp = myfun_2(cell_args)
    % geometric mean
    [input_1, input_2] = cell_args{:};
    
    resp    = sqrt(input_1 * input_2);
end % endfun myfun_2
function resp = myfun_3(cell_args)
    % arithmetic-geometric mean: agm
    [a,g] = cell_args{:}; % [input_1,input_2]
    for ii = 1:10 % 10 iterations
        a = myfun_1({a,g});
        g = myfun_2({a,g});
    end %endfor
    
    resp = {a,"4"} ;
end % endfun myfun_3