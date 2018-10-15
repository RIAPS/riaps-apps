clc
clear all

%% Params
data_fp = '#Data';
% data_fn = 'cs01_no_ls.csv';
% mat_fn = 'cs01_no_ls.mat';

% data_fn = 'cs01_no_ls_[Video record].csv';
% mat_fn = 'cs01_no_ls_[Video record].mat';

data_fn = 'cs01_with_dufls_[VR].csv';
mat_fn = 'cs01_with_dufls_[VR].mat';

%% 
data_preprocessing( data_fp, data_fn, mat_fn );
