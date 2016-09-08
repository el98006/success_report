'''
Created on Jul 14, 2016

@author: eli
'''

from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator
import datetime
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
import util 
import logging

NUM_WEEKS = 20

Y_MARGIN = 1

'''
date_since,  date type, is the 1st day (Sunday) of the week where DB query starts with
if date_since is None, then starting with 20 weeks back until 1st day of current week.
'''

def generator_weekly_data(db_config, date_since = None):
    
    end = datetime.date.today()
    day1_of_ending_week = end - datetime.timedelta(days=end.weekday()+1)
    
    
    
    if date_since: 
        day1_of_starting_week = date_since
    else:
        day1_of_starting_week = day1_of_ending_week - NUM_WEEKS * datetime.timedelta(days=7) 
      
    
    while day1_of_starting_week < day1_of_ending_week: 
        col = []
        div = []
        str_start = day1_of_starting_week.strftime('%d-%b-%Y')
        str_end = (day1_of_starting_week + datetime.timedelta(days=6)).strftime('%d-%b-%Y')
        print str_start
        col.append(str_start)
        for d in util.map_div_to_type.keys():
            d1 = util.get_tx_count(db_config, str_start, str_end, d,False) 
            d2 = util.get_tx_count(db_config, str_start, str_end, d, True)
            d3 = '{:.1f}'.format(float(d2) / float(d1) * 100)
            col.append(d1)
            col.append(d2)
            col.append(d3)
            div.append(d)
        yield (col, div)
        day1_of_starting_week +=  datetime.timedelta(days=7)


def format_y(value,pos):
    return '{:,.0f}'.format(value)
        
def render_data(input_matrix, index_no, div_no):
    color_map =['#4F88BE','#008032','#C82121']
    bar_width = 0.2 
    fig = plt.figure()
    #horizontal_alignment options
    ha = ['left', 'center', 'right']

    ''' 2nd Y axis is plot for success rate, percentage, from 0% to 100% '''
    
    ax = fig.add_subplot(111)
    ax2 =  ax.twinx()
    
    #add 0.15 inch to the bottom of the plots to accomodate longer x-labels
    fig.subplots_adjust(bottom = 0.15)
    
    # each division takes 3 columns, series 1 takes columm 1, 2, and 3, series 2 takes, 4,5, and 6, in turn
    col_nums = np.arange(3) + 1 + 3 * index_no
    
    ax.set_ylabel('TX') 
    # ax.margins(0.05, None) set margins on y axis
    # ax.margins(None, 0.5)
    bar_pos_series = np.arange(len(input_matrix)) + Y_MARGIN
    '''
    bar(list_position, list_of height, width, color)
    list_position: list of position on the x_axis, 
    list_height: data series 
    '''
    
    bar1 = ax.bar(bar_pos_series, input_matrix[:,col_nums[0]], bar_width,color=color_map[0])
    bar2 = ax.bar(bar_pos_series + bar_width,  input_matrix[:,col_nums[1]], bar_width, color=color_map[1])
    
   
    ''' 
    formatter = FuncFormatter(format_y)
    ax.yaxis.set_major_formatter(formatter)

    To manually set up Y Axis ticks
    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(start, end, 10000))
    '''
    
    '''
    To specify a fixed number of minor internals per major interval, set the properties of the ticks.
    '''
    minorLocator = AutoMinorLocator(5) 
    ax.yaxis.set_minor_locator(minorLocator)
    plt.tick_params(which='minor', length=4, width=3, color ='black')
    
    
    '''plot the success rate on ax2'''
    ax2.set_ylim(0,100)
    ax2.plot(input_matrix[:,col_nums[2]], color=color_map[2], linewidth=2,marker=Line2D.filled_markers[1], markersize=10) 
    ax2.set_ylabel('success rate %',color=color_map[2])
    for tl in ax2.get_yticklabels():
        tl.set_color(color_map[2])
        
    ax.set_xticks(np.arange(len(input_matrix) + Y_MARGIN ))
    ax.set_xticklabels(input_matrix[:,0], rotation=45, ha = 'right', size = 8)
    
    fig.legend( [bar1[0],  bar2[0], ax2.lines[0]],['Total Tx','Successful Tx','success rate'])

    plt.title( div_no + ' Weekly Transaction Success'  )
    plt.grid(True)
    plt.show()



           


def load_history_data(file_name):
    full_path = os.path.join(os.path.dirname(__file__), file_name)
    
    if not os.path.exists(full_path):
        print 'no history file, creating a empty one'
        return False
    with open(full_path,'rb') as fh:
        array_history = pickle.load(fh)
    return array_history

        
        
if __name__ == '__main__':

    db_config, data_file_name = util.load_config()
    
    history_data =  load_history_data(data_file_name)
    
    if history_data: 
        previous_date = history_data[-1][0]
        # compare the date of most recent history data to the 1st day of current week, if the same, it's update to date, no need to run the query, otherwise 
        # a generator is returned contains tuples of (new data, list of divisions) 
        if datetime.date.today() - util.str_to_date(previous_date) > datetime.timedelta(days = 6):
            gen_tuple_data_div = generator_weekly_data(db_config, date_since = util.str_to_date(previous_date))
        else:
            gen_tuple_data_div = False
    else:
        #first time run, there is no pickle file created to hold the history data, 
        history_data = []
        gen_tuple_data_div = generator_weekly_data(db_config)
    
    for new_data, list_of_divisions in gen_tuple_data_div:
        history_data.append(new_data)
    
    with open(data_file_name,'wb') as fh:
        pickle.dump(history_data,fh)
    
    for index, div_no in enumerate(list_of_divisions):
        render_data(np.array(history_data), index, div_no)
 
    print "completed successfully"
    