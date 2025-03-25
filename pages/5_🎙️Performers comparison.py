# -*- coding: utf-8 -*-
"""
This module defines the streamlit application
"""

import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from src.durations_analyse_tools import *
from src.data import *
from src.stats import *

#############################
# PAGE CONFIG
#############################

def config_page():
    st.set_page_config(layout="wide", page_title="Comparison beetween performers on the entire corpus", page_icon="🎙️")

config_page()

    

#############################
# boxplots
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
                     va='top', transform=axs.get_xaxis_transform(), fontsize=25)
            i+=7
        custom_lines = [Line2D([0], [0], color=colors[i], lw=4) for i in range(len(colors))]
        axs.legend(custom_lines, [p[0].upper()+p[1:] for p,t in PERFORMERS_AND_TUNING], 
                   fontsize=20, ncols=6)
    else:
        axs.tick_params(axis='x', labelsize=12)
    if metric != 'ioiratios': 
        plt.axhline(y=0, color='gray', linestyle='--')
    else:
        plt.axhline(y=1, color='gray', linestyle='--')
    
    axs.grid(True, linestyle='--')
    axs.set_ylabel("$\Delta \mathit{IOI}$", fontsize=30, labelpad=25, rotation=0)
    #axs.set_ylim(-0.15, 0.19)
    axs.tick_params(axis='y', labelsize=30)  # Taille des labels des ticks
    form.pyplot(plt.gcf())
    plt.savefig(f'{GRAPHS}/boxplotperformer{perfnames}.png')
        


##############################
# pages functions
##############################


#def performers_global_ratios():
#    """Boxplots comparing the 6 performers timing ioi ratios on several features
#    """
#    st.write("# Box plots  of ioi ratios by performers and grouped by selected categories")
#    st.write("$ioi\_ratios = \dfrac{ioi}{metronomic\_ioi}$")
#    
#    with st.spinner("Wait for it....", show_time=True):
#        if 'all_performers_ioi' not in st.session_state:
#            all_performers_ioi=timings('ioiratios')
#            st.session_state.all_performers_ioi=all_performers_ioi
#            st.toast('Done!', icon='🎉')
#    form_all_ratios = st.form("form_all_ratios")
#    with form_all_ratios:# voir session state pour 
#        options=st.multiselect(
#            "Select filters:",
#            list(st.session_state.all_performers_ioi['kuijken'].keys())
#        )
#        submitted = form_all_ratios.form_submit_button("Display Box plots")
#        if submitted:    
#            cmap = plt.get_cmap('Accent')
#            colors = [cmap(i / 7) for i in range(6)]
#            x=[]
#            for k in options:
#                x += [st.session_state.all_performers_ioi[p][k] 
#                      for p in st.session_state.all_performers_ioi.keys()]
#            fig, ax = plt.subplots(figsize=(9, 4))
#            box_plot_show(x, options, colors, 
#                          form_all_ratios, metric='ioiratios')


def performers_global_deltaioi():
    """Boxplots comparing the 6 performers deltas ioi per measure on several features
    """
    st.write("# Box plots  of delta ioi per measure by performers and grouped by selected categories")
    st.write("$\Delta ioi_{measure} = \dfrac{(ioi-metronomic\_ioi)}{measure\_duration}$")    
         
    with st.spinner("Wait for it....", show_time=True):
        if 'all_performers_deltas_ioi' not in st.session_state:
            all_performers_deltas_ioi=timings('deltaioi')
            st.session_state.all_performers_deltas_ioi=all_performers_deltas_ioi
            st.toast('Done!', icon='🎉')
    form_all_deltas_ioi = st.form("form_all_deltas_ioi")
    with form_all_deltas_ioi:# voir session state pour 
        options_deltas_ioi=st.multiselect(
            "Select filters:",
            list(st.session_state.all_performers_deltas_ioi['kuijken'].keys())
        )
        submitted_deltas_ioi = form_all_deltas_ioi.form_submit_button("Display Box plots")
        if submitted_deltas_ioi:    
            cmap = plt.get_cmap('Accent')
            colors = [cmap(i / 7) for i in range(6)]
            x=[]
            for k in options_deltas_ioi:
                x += [st.session_state.all_performers_deltas_ioi[p][k] 
                      for p in st.session_state.all_performers_deltas_ioi.keys()]
            fig, ax = plt.subplots(figsize=(9, 4))
            box_plot_show(x, options_deltas_ioi, colors,
                          form_all_deltas_ioi, metric='deltaioi')


def performers_global_deltaonset():
    """Boxplots comparing the 6 performers deltas onset per measure on several features
    """
    st.write("# Box plots  of deltas onset per measure by performers and grouped by selected categories")
    st.write("$\Delta onsets_{measure} = \dfrac{(onset-metronomic\_onset)}{measure\_duration}$")    
         
    with st.spinner("Wait for it....", show_time=True):
        if 'all_performers_deltas_onset' not in st.session_state:
            all_performers_deltas_onset=timings('deltaonset')
            st.session_state.all_performers_deltas_onset=all_performers_deltas_onset
            st.toast('Done!', icon='🎉')
    form_all_deltas_onset = st.form("form_all_deltas_onset")
    with form_all_deltas_onset:# voir session state pour 
        options_deltas_onset=st.multiselect(
            "Select filters:",
            list(st.session_state.all_performers_deltas_onset['kuijken'].keys())
        )
        submitted_deltas_onset = form_all_deltas_onset.form_submit_button("Display Box plots")
        if submitted_deltas_onset:    
            cmap = plt.get_cmap('Accent')
            colors = [cmap(i / 7) for i in range(6)]
            x=[]
            for k in options_deltas_onset:
                x += [st.session_state.all_performers_deltas_onset[p][k] 
                      for p in st.session_state.all_performers_deltas_onset.keys()]
            fig, ax = plt.subplots(figsize=(9, 4))
            box_plot_show(x, options_deltas_onset, colors, 
                          form_all_deltas_onset, metric='deltaonset')         
            
            
####################
## layout
####################

page_names_to_funcs = {
    #"IOI ratios":performers_global_ratios,
    "ΔIOI per measure": performers_global_deltaioi,
    "Δonsets per measure": performers_global_deltaonset
}

select = st.sidebar.selectbox("Choose a visualisation", page_names_to_funcs.keys())
page_names_to_funcs[select]()