clc
clear all
close all

%% Params for plot settings
axis_range_vec = [-0.1 20 52.2 60.2];
FONT_SIZE=12;
legend_str_cell={'No Load Shedding','With Distributed UFLS (RAS-2)'};

%%
hf = figure();
hold on
grid on

plot_curve('cs01_no_ls_[Video record].mat', 'r')
% plot_curve('cs01_with_cufls_[VR].mat', 'g')
plot_curve('cs01_with_dufls_[VR].mat', 'b')

%% Setting
axis(axis_range_vec)
legend(legend_str_cell)

set(gca,'Fontsize',FONT_SIZE,'FontWeight','bold')
% title('Comparison of two load shedding methods','FontWeight','bold','FontSize',FONT_SIZE)
xlabel('Time (S)','FontWeight','bold','FontSize',FONT_SIZE)
ylabel('Frequency (Hz)','FontWeight','bold','FontSize',FONT_SIZE)
