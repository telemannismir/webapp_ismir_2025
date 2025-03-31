# -*- coding: utf-8 -*-
"""
This module defines the streamlit application
"""

import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from src.durations_analyse_tools import *
from src.data import *
from src.stats import *
from src.streamlit_displays import display_tab

#############################
# PAGE CONFIG
#############################

def config_page():
    st.set_page_config(layout="wide", page_title="Analyse by type of Movment", page_icon="🕺🏼")


#############################
# plots
#############################



def ticks_positions(n: int)->list[int]:
    """Compute ticks position for group of 6 box plots 

    Args:
        n: total number of box plots

    Returns:
        positions of the grouped ticks labels in the graph
    """
    res = []
    i, c= 1, 0
    while c < n:
        res.append(i)
        c += 1
        if c % 6 == 0: i += 2
        else: i += 1
    return res


def box_plot_show(x, options, colors, form, perfnames='all', metric='ioiratios'):
    if perfnames!='all':
        fig, axs = plt.subplots(figsize=(9, 4))
        tick_labels=options
        positions=range(len(options))  
    else:
        fig, axs = plt.subplots(figsize=(20,10))
        n_labels=len(colors)*len(options)
        tick_labels=n_labels*[' ']
        positions=ticks_positions(len(x))
    bplot = plt.boxplot(x, tick_labels=tick_labels,
                            positions=positions,
                           showmeans=True, 
                           showfliers=False,  
                           patch_artist=True,
                           medianprops = dict(color = "blue", linewidth = 1.5),
                           meanprops={"marker": "+","markeredgecolor": "black", "markersize": "5"},
                        )
    for i in range(len(bplot['boxes'])):
        bplot['boxes'][i].set(facecolor = colors[i%len(colors)], linewidth=2)
    # Add label for a group of 6 ticks
    if perfnames=='all':
        axs.tick_params(axis = 'x', length = 0)
        i=0
        for k in options:
            pos = 3.5 + i
            axs.text(pos, -0.02, k, ha='center',
                     va='top', transform=axs.get_xaxis_transform(), fontsize=18)
            i+=7
        custom_lines = [Line2D([0], [0], color=colors[i], lw=4) for i in range(len(colors))]
        axs.legend(custom_lines, [p for p,t in PERFORMERS_AND_TUNING], 
                   fontsize=12, ncols=6)
    else:
        axs.tick_params(axis='x', labelsize=12)
    if metric != 'ioiratios': 
        plt.axhline(y=0, color='gray', linestyle='--')
    else:
        plt.axhline(y=1, color='gray', linestyle='--')
    
    form.pyplot(plt.gcf())
    plt.savefig(f'{GRAPHS}/boxplotperformer{perfnames}.png')
        


##############################
# main function
##############################
    
def by_movements(): 
    st.header("Analyse by type of Movment and by performer on all the corpus")
    # call back to update options for box plot
    def pill_callback():
        for key in st.session_state.keys():
            del st.session_state[key]
            
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    with st.container(border=True):
        names = [p for p,t in PERFORMERS_AND_TUNING]
        performer= st.pills("choose a performer", names, default='kuijken', on_change=pill_callback)
        metric= st.pills("choose a metric", ['deltaonset', 'deltaioi'], default='deltaioi', on_change=pill_callback)
        movement_name=st.selectbox("choose a type of movement", MOVEMENTS_POSITIONS.keys(), on_change=pill_callback)
    
    if 'performers_metric_results' not in st.session_state:
        metric_all, data_all = get_all_metric_and_data_for_one_performer(performer, metric=metric, movement_name= movement_name)
        ####### dataframe with raw data and ioi_ratios ######################
        dfdata = pd.DataFrame.from_dict(data_all)
        dfdata[metric]=metric_all
        st.session_state.dfdata=dfdata
        ######################################################################
    # display stats
        performers_metric_results=timings(metric, performer, metric_all, data_all)
        st.session_state.performers_metric_results = performers_metric_results
        statistics= results_to_stats(st.session_state.performers_metric_results[performer])
        st.session_state.statistics = statistics
    
    for f in MOVEMENTS_POSITIONS[movement_name]:
        
        st.write(f"Fantasia {f} -- movement(s) n°: {'-'.join([str(n) for n in MOVEMENTS_POSITIONS[movement_name][f]])}")
        
    N=len(st.session_state.statistics)
    display_tab(st.session_state.statistics, metric=metric)
    

    with st.expander("See data"):
        st.session_state.dfdata
        
    form_fantasia = st.form("form_fantasia")
    with form_fantasia:# voir session state pour 
        options=st.multiselect(
            "Select filters:",
            list(st.session_state.statistics.keys())
        )
        submitted = form_fantasia.form_submit_button("Display Box plot")
        if submitted:
            x= [st.session_state.performers_metric_results[performer][k] for k in options]
            cmap = plt.get_cmap('tab20c')
            colors = [cmap(i / (N-1)) for i in range(N)]
            box_plot_show(x, options, colors, form_fantasia, 
                        perfnames=performer, metric=metric)


##############################
# on load
##############################

config_page()
by_movements()