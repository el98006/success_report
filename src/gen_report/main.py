'''
Created on Jul 14, 2016

@author: eli
'''

#from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
import util 
import logging

NUM_WEEKS = 20

# add margin to x and y directions in terms
X_MARGIN = 0.05
Y_MARGIN = 0  


'''
date_since,  date type, is the 1st day (Sunday) of the week where DB query starts with
if date_since is None, then starting with 20 weeks back until 1st day of current week.
for longer history, change NUM_WEEKS with number > 20
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
     
        logger.info(('start %s,  end %s') %(str_start, str_end))
        col.append(str_start)
        for d in util.map_div_to_type.keys():
            d1 = util.get_tx_count(db_config, str_start, str_end, d,False) 
            d2 = util.get_tx_count(db_config, str_start, str_end, d, True)
            d3 = '{:.1f}'.format(float(d2) / float(d1) * 100)
            col.append(d1)
            col.append(d2)
            col.append(d3)
            logger.info('total Tx: %s, Succ Tx: %s, Succ Rate %s' %(d1, d2, d3))
            div.append(d)
        yield (col, div)
        day1_of_starting_week +=  datetime.timedelta(days=7)


def format_y(value,pos):
    return '{:,.0f}'.format(value)
        
def render_data(input_matrix, index_no, div_no, rec_no=NUM_WEEKS):
    color_map =['#4F88BE','#008032','#C82121']
    bar_width = 0.2 
    fig = plt.figure()
    #horizontal_alignment options
    #ha = ['left', 'center', 'right']

    ''' 2nd Y axis is plot for success rate, percentage, from 0% to 100% '''
    
    ax = fig.add_subplot(111)
    ax2 =  ax.twinx()
    
    #add 0.15 inch to the bottom of the plots to accomodate longer x-labels
    fig.subplots_adjust(bottom = 0.15)
    
    # each division takes 3 columns, series 1 takes column 1, 2, and 3, series 2 takes, 4,5, and 6, in turn
    col_nums = np.arange(3) + 1 + 3 * index_no
    
    ax.set_ylabel('TX') 
    # ax.margins(x-padding, y-padding)
    # manually set tick positions, and bar positions, better solution is to control margin at the plot/subplot level.
    #bar_pos_series = np.arange(len(input_matrix)) + X_MARGIN
    bar_pos_series = np.arange(rec_no) if rec_no < len(input_matrix) else np.arange(len(input_matrix))

    #bar_pos_series = if len(input_matrix) np.arange(len(input_matrix)) 
    '''
    bar(list_position, list_of height, width, color)
    list_position: list of position on the x_axis, 
    list_height: data series 
    '''

    print bar_pos_series
    bar1 = ax.bar(bar_pos_series, input_matrix[-rec_no:,col_nums[0]], bar_width,color=color_map[0])
    bar2 = ax.bar(bar_pos_series + bar_width,  input_matrix[-rec_no:,col_nums[1]], bar_width, color=color_map[1])
    
   
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
    ax2.plot(input_matrix[-rec_no:,col_nums[2]], color=color_map[2], linewidth=2,marker=Line2D.filled_markers[1], markersize=10) 
    ax2.set_ylabel('success rate %',color=color_map[2])
    for tl in ax2.get_yticklabels():
        tl.set_color(color_map[2])
        
    #ax.set_xticks(np.arange(len(input_matrix) + Y_MARGIN ))
    ax.set_xticks(bar_pos_series)
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticklabels(input_matrix[-rec_no:,0], rotation=45, ha = 'right', size = 8)
    
    fig.legend( [bar1[0],  bar2[0], ax2.lines[0]],['Total Tx','Successful Tx','success rate'])

    plt.title( div_no + ' Weekly Transaction Success'  )
    plt.grid(True)
    
    # add padding horizontally, vertically,
    plt.margins(X_MARGIN, Y_MARGIN)
    plt.show()



           


def load_history_data(file_name):
    full_path = os.path.join(os.path.dirname(__file__), file_name)
    logger = logging.getLogger('root.load_history_data')
    if not os.path.exists(full_path):
        logger.info( 'no history file, creating a empty one')
        return False
    with open(full_path,'rb') as fh:
        payload = pickle.load(fh)
    return payload['data'], payload['divisions']

def update_data_file(file_name, data, divisions): 
    with open(file_name,'wb') as fh:
        payload = {}
        payload['divisions'] = divisions
        payload['data'] = data
        pickle.dump(payload,fh)       
        

def init_logging():
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    
    fh = logging.FileHandler('success_report.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def de_dupe(history_data):    
    history_data, divisions = history_data
    
    rec_no = len(history_data) 
    cnt = 0
    date_list = []
    clean_rec = []
    for r  in history_data:
        if r[0] not in date_list:
            date_list.append(r[0])
            clean_rec.append(r)
            cnt += 1
        else:
            logger.info('duplicate records on {}'.format(r[0]))
    print clean_rec
    logger.info('de_dupe before{}, after{}'.format(rec_no, cnt))
    return clean_rec, divisions        

if __name__ == '__main__':

    db_config, data_file_name = util.load_config()
   
    logger = init_logging();
    logger.info("log started")
    
   
    history_check_result = load_history_data(data_file_name)
    
    # turn it on  when needed
    # history_check_result = de_dupe(history_check_result)

    
    if history_check_result: 
        history_data, list_of_divisions =  history_check_result 
        previous_date = history_data[-1][0]
        logging.info('load history data, most recent data on day of{}'.format(previous_date))
        # compare the date of most recent history data to the 1st day of current week, if the same, it's update to date, no need to run the query, otherwise 
        # a generator is returned contains tuples of (new data, list of divisions) 
        if datetime.date.today() - util.str_to_date(previous_date) > datetime.timedelta(days=13):
                                                                                       
            logger.info('getting data since {} from DB'.format(previous_date))
            gen_tuple_data_div = generator_weekly_data(db_config, date_since = util.str_to_date(previous_date))
        else:
            logger.info('last reporting date {}, run report 7 days after '.format(previous_date))
            update_history = False
            logger.info ('no new data, exiting')
        
    else:
        #first time run, there is no pickle file created to hold the history data, 
        history_data = []
        gen_tuple_data_div = generator_weekly_data(db_config)
        update_history = True
    # if there new data update, append to data_matrix
 
    if update_history: 
        for new_rec, division in gen_tuple_data_div:
            history_data.append(new_rec)
            if division not in list_of_divisions:
                list_of_divisions.append(division)
            logger.info('append data to histoy data')
        update_data_file(data_file_name, history_data, list_of_divisions)
        '''    
        with open(data_file_name,'wb') as fh:
            pickle.dump(history_data,fh)
        '''
    for index, div_no in enumerate(list_of_divisions):
        render_data(np.array(history_data), index, div_no, rec_no=30)
 
    logger.info( "completed successfully")
    
    
