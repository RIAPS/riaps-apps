function [ ] = plot_curve( mat_fpn, color_str )
%PLOT_CURVE Summary of this function goes here
%   Detailed explanation goes here

LWidth = 2;
ind_shift = 100;

%%
load(mat_fpn);

evt_ind = find(freq_vec<60,1);
start_plot_ind = evt_ind - ind_shift;
if start_plot_ind <= 0
    start_plot_ind = 1;
end

time_vec = time_vec - time_vec(start_plot_ind);
plot(time_vec(start_plot_ind:end), freq_vec(start_plot_ind:end), color_str, 'LineWidth', LWidth);

end

