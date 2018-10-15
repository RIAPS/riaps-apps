function data_preprocessing( data_fp, data_fn, mat_fn )
%DATA_PREPROCESSING Summary of this function goes here
%   Detailed explanation goes here

%% Import & Process
data_fpn = fullfile(data_fp, data_fn);

no_ls_data_struc = importdata(data_fpn);
freq_vec = no_ls_data_struc.data(:,1);
load_mat = no_ls_data_struc.data(:,2:end);
time_cell = no_ls_data_struc.textdata;

time_vec = zeros(size(time_cell));
for i=1:numel(time_cell)
    cur_datetime_str = time_cell{i};
    
    temp_cell = strsplit(cur_datetime_str);
    cur_time_str = temp_cell{2};
    
    cur_time_cell = strsplit(cur_time_str,'.');
    cur_time_ms = str2double(cur_time_cell{2});
    cur_time_hms_cell = strsplit(cur_time_cell{1},':');
    cur_time_h = str2double(cur_time_hms_cell{1});
    cur_time_m = str2double(cur_time_hms_cell{2});
    cur_time_s = str2double(cur_time_hms_cell{3});
    
    cur_time_total_s = cur_time_h*60*60 ...
    + cur_time_m*60 + cur_time_s + cur_time_ms/1e3;
    
    time_vec(i) = cur_time_total_s;
end

%% Save
save(mat_fn, 'time_vec', 'freq_vec', 'load_mat')

end

