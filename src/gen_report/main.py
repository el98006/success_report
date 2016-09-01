'''
Created on Jul 14, 2016

@author: eli
'''
from util import get_tx_count, map_div_to_type
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from datetime import timedelta, datetime,date
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from gen_report.util import load_config

NUM_WEEKS = 52

def gen_weekly_data(db_config):
    end = date.today()
    start = end - timedelta(days=end.weekday()+1)
    
    for i in range(NUM_WEEKS):
        col = []
        start = start - timedelta(days=7)
        end  = start + timedelta(days=6)
        str_start = start.strftime('%d-%b-%Y')
        str_end = end.strftime('%d-%b-%Y')
        print str_start
        col.append(str_start)
        for d in map_div_to_type.keys():
            d1 = get_tx_count(str_start, str_end, d,False) 
            d2 = get_tx_count(str_start, str_end,d, True)
            d3 = '{:.1f}'.format(float(d2) / float(d1) * 100)
            col.append(d1)
            col.append(d2)
            col.append(d3)
        yield (col)

def save_report(input):

    fname = datetime.today().strftime('%Y%m%d') + '.csv'
    user_dir = os.path.expanduser('~')
    fulln = os.path.join(user_dir,fname)
    with open(fulln, 'wb') as fh:
        csvh = csv.writer(fh)
        header = ['Week']
        for i in map_div_to_type.keys():
            header.append(i +'Total')
            header.append(i +'Success' )
            header.append(i + ' %')
        csvh.writerow(header)
        for row in input: 
            csvh.writerow(row)

def get_data():
    raw_data = []
    x_label =[]
    my_path = os.path.expanduser('~')
    f_path = os.path.join(my_path,'20160816.csv')
    with open(f_path,"rb") as fh:
        csv_reader = csv.reader(fh)
        header = True
        for row in csv_reader:
            if header: 
                data_series = row
                header = False
                continue
            
            x_label.append(row[0])
            raw_data.append( [ col for col in row[1:] ])
   
    return (x_label, data_series,raw_data)

def format_y(value,pos):
    return '{:,.0f}'.format(value)
    
    
    
def  draw_chart(x_label,input_matrix):
    
    color_map =['#4F88BE','#008032','#C82121']
    bar_width = 0.2 
    fig = plt.figure()
    #horizontal_alignment
    ha = ['left', 'center', 'right']
    
    ax = fig.add_subplot(111)
    ax2 =  ax.twinx()
    
    #ax.plot(input_matrix[:,6::1])
    ax.set_ylabel('TX')
    bar1 = ax.bar(np.arange(len(x_label)),input_matrix[:,6], bar_width,color=color_map[0])
    bar2 = ax.bar(np.arange(len(x_label)) + bar_width, input_matrix[:,7],bar_width, color=color_map[1])
    formatter = FuncFormatter(format_y)
    ax.yaxis.set_major_formatter(formatter)
    start, end = ax.get_ylim()
    #ax.yaxis.set_ticks(np.arange(start, end, 10000))
    minorLocator = AutoMinorLocator()
    #specify a fixed number of minor internals per major internval minorLocator=AutoMinorLocator(2) 
    ax.yaxis.set_minor_locator(minorLocator)
    
    plt.tick_params(which='minor', length=4, width=3, color ='black')
    ax2.set_ylim(0,100)
    ax2.plot(input_matrix[:,8], color=color_map[2], linewidth=2,marker=Line2D.filled_markers[1], markersize=10) 
    ax2.set_ylabel('success rate %',color=color_map[2])
    for tl in ax2.get_yticklabels():
        tl.set_color(color_map[2])
    ax.set_xticks(np.arange(len(x_label) ))
    ax.set_xticklabels(x_label, rotation=45, ha='right')
    fig.legend( [bar1[0],  bar2[0], ax2.lines[0]],['Total Tx','Successful Tx','success rate'])

    plt.title('Weekly Transaction Success')
    plt.grid(True)
    plt.show()
    
if __name__ == '__main__':
    db_config = load_config()
    gen_weekly_data(db_config)
    #db_result = gen_weekly_data()
    #draw_chart(db_result)
    #save_report(db_result)
    x_label, data_series, plot_data = get_data()
    my_mat = np.array(plot_data)
    draw_chart(x_label, my_mat)
    
    print "completed successfully"
    