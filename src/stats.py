from statistics import mean, quantiles, pstdev
from src.durations_analyse_tools import *

#####################################
#ioi
######################################

def get_metric_of_selected_elements(metric_data:list[float], 
                                 data: list[dict[str:str]], 
                                 rest_filtered: bool=False, 
                                 select_voice: str=None, 
                                 d: float=None, 
                                 beats_indexes: list[float]=None)->list:
    """Returns a list of filtered results within a sequence 

    Args:
        metric_data : sequence of ioiratios or deltaioi or deltaonset
        data : 
        rest_filtered: False if rests are take into account, True otherwise 
        select_voice: voice selected
        d : (in quarter note) None if all durations, otherwise filter on a specific duration for only notes (not rest)
        beats_indexes: None if all elements used

    Returns:
        sequence of filtered results
    """
    tab=[]
    ## sequence of indexes depending on beats:
    if beats_indexes==None:
        beats_indexes = range(len(data))
    ## all durations    
    if d==None :
        if rest_filtered:
            tab = [metric_data[i] for i in beats_indexes if data[i]['voice']!='.']
        elif select_voice!=None:
            tab = [metric_data[i] for i in beats_indexes if data[i]['voice'] in select_voice]
        else:
            tab = metric_data
    ## specific duration    
    elif d!=None :
        if rest_filtered:
            tab = [metric_data[i] for i in beats_indexes if (data[i]['duration']==str(d) and data[i]['voice']!='.')]
        elif select_voice!=None:
            tab = [metric_data[i] for i in beats_indexes if (data[i]['duration']==str(d) and data[i]['voice'] in select_voice)]
        else:
            tab = [metric_data[i] for i in beats_indexes if data[i]['duration']==str(d)]      
    return tab


def get_metric_results(metric_data: list[float], datas: list[str])->dict[str:list[float]]:
    """_summary_

    Returns:
        _description_
    """
    results=dict()
    # get list of measures positions in float
    measures_positions = get_positions_in_measures_fractions(datas)
    # get indexes of beats (on/off/first)
    on_beats = filtered_beats_indexes(datas, measures_positions, 'on')
    off_beats = filtered_beats_indexes(datas, measures_positions, 'off')
    first_beats = filtered_beats_indexes(datas, measures_positions, 'first')
    
    #binary_indexes_on=[i for i in on_beats if datas[i]['time_signature'] in BINARY_TS]
    #binary_indexes_off=[i for i in off_beats if datas[i]['time_signature'] in BINARY_TS]
    #ternary_indexes_on=[i for i in on_beats if datas[i]['time_signature'] in TERNARY_TS]
    #ternary_indexes_off=[i for i in off_beats if datas[i]['time_signature'] in TERNARY_TS]
    
    
    
    #for sixteenth notes in position 1,2,3,4 of a group of 4 in binary meter 2/4, 3/4 and 4/4
    sixteenth_p1_indexes= get_binary_sixteenth_indexes(datas, measures_positions, 1)
    
    ###########interleaved sixteenth notes stats#############################
    #res={}
    #for i in sixteenth_p1_indexes:
    #    res[i]=datas[i]['voice']+datas[i+1]['voice']+datas[i+2]['voice']+datas[i+3]['voice']
    #print(res)
    ##########################################################################
    
    sixteenth_p2_indexes= get_binary_sixteenth_indexes(datas, measures_positions, 2)
    sixteenth_p3_indexes= get_binary_sixteenth_indexes(datas, measures_positions, 3)
    sixteenth_p4_indexes= get_binary_sixteenth_indexes(datas, measures_positions, 4)

    #for eight notes in position 1,2,3 of a group of 3 in ternary meter 3/8, 6/8, 9/8 and 12/8
    eight_ternary_p1_indexes= get_ternary_eight_indexes(datas, measures_positions, 1)
    eight_ternary_p2_indexes= get_ternary_eight_indexes(datas, measures_positions, 2)
    eight_ternary_p3_indexes= get_ternary_eight_indexes(datas, measures_positions, 3)
    
    #for eight notes in position 1,2 of a group of 2 with interleaved voices in binary meter 2/4, 3/4 and 4/4
    eight_interleaved_p1= get_binary_eight_interleaved_indexes(datas, measures_positions, 1)
    eight_interleaved_p2= get_binary_eight_interleaved_indexes(datas, measures_positions, 2)
    
    #for eight notes in position 1,2 of a group of 2 with no voice in binary meter 2/4, 3/4 and 4/4
    eight_no_interleaved_p1= get_binary_eight_not_interleaved_indexes(datas, measures_positions, 1)
    eight_no_interleaved_p2= get_binary_eight_not_interleaved_indexes(datas, measures_positions, 2)
    
    #####results
    results['all']=get_metric_of_selected_elements(metric_data, datas)
    results['no rest']=get_metric_of_selected_elements(metric_data, datas,  rest_filtered=True)
    # voice
    results['B']=get_metric_of_selected_elements(metric_data, datas,  select_voice='B')
    results['b']=get_metric_of_selected_elements(metric_data, datas,  select_voice='bs')
    results['Bb']=get_metric_of_selected_elements(metric_data, datas,  select_voice='Bb')
    results['S']=get_metric_of_selected_elements(metric_data, datas,  select_voice='S')
    results['T']=get_metric_of_selected_elements(metric_data, datas,  select_voice='T')
    results['x']=get_metric_of_selected_elements(metric_data, datas,  select_voice='x')
     # just for quarter note
    results['♩']=get_metric_of_selected_elements(metric_data, datas,  rest_filtered=True, d=1.0)
    # just for eighth note
    results['♪']=get_metric_of_selected_elements(metric_data, datas,  rest_filtered=True, d=0.5)
    # just for sixteenth note
    results['♬']=get_metric_of_selected_elements(metric_data, datas,  rest_filtered=True, d=0.25)
    
    results['1st beat']=get_metric_of_selected_elements(metric_data, datas, 
                                                     rest_filtered=True, beats_indexes=first_beats)
   ##meter
   #results['on binary']=get_metric_of_selected_elements(metric_data, datas,  
   #                                                 rest_filtered=True, beats_indexes=binary_indexes_on)
   #results['off binary']=get_metric_of_selected_elements(metric_data, datas,  
   #                                                  rest_filtered=True, beats_indexes=binary_indexes_off)
   #results['on ternary']=get_metric_of_selected_elements(metric_data, datas, 
   #                                                  rest_filtered=True, beats_indexes=ternary_indexes_on)
   #results['off ternary']=get_metric_of_selected_elements(metric_data, datas, 
   #                                                   rest_filtered=True, beats_indexes=ternary_indexes_off)
   ##8th note : beat
   #results['♪ on']=get_metric_of_selected_elements(metric_data, datas,  
   #                                             rest_filtered=True, d=0.5, beats_indexes=on_beats)
   #results['♪ off']=get_metric_of_selected_elements(metric_data, datas,  
   #                                              rest_filtered=True, d=0.5, beats_indexes=off_beats)
   ##8th note : voice + beat
   #results['♪x on']=get_metric_of_selected_elements(metric_data, datas, 
   #                                              select_voice='x', d=0.5, beats_indexes=on_beats)
   #results['♪x off']=get_metric_of_selected_elements(metric_data, datas,
   #                                               select_voice='x', d=0.5, beats_indexes=off_beats)
   #
   #results['♪S on']=get_metric_of_selected_elements(metric_data, datas,  
   #                                              select_voice='S', d=0.5, beats_indexes=on_beats)
   #results['♪S off']=get_metric_of_selected_elements(metric_data, datas, 
   #                                               select_voice='S', d=0.5, beats_indexes=off_beats)
   #results['♪Bb on']=get_metric_of_selected_elements(metric_data, datas, 
   #                                               select_voice='Bb', d=0.5, beats_indexes=on_beats)
   #results['♪Bb off']=get_metric_of_selected_elements(metric_data, datas, 
   #                                                select_voice='Bb', d=0.5, beats_indexes=off_beats)
   #results['♪b on']=get_metric_of_selected_elements(metric_data, datas, 
   #                                              select_voice='bs', d=0.5, beats_indexes=on_beats)
   #results['♪b off']=get_metric_of_selected_elements(metric_data, datas, 
   #                                            select_voice='bs', d=0.5, beats_indexes=off_beats)   
   #
    results['on beat']=get_metric_of_selected_elements(metric_data, datas, 
                                                    rest_filtered=True, beats_indexes=on_beats)
    
    results['♪ on']=get_metric_of_selected_elements(metric_data, datas,  
                                                rest_filtered=True, d=0.5, beats_indexes=on_beats)
    results['off beat']=get_metric_of_selected_elements(metric_data, datas, 
                                                     rest_filtered=True, beats_indexes=off_beats)
    results['♪ off']=get_metric_of_selected_elements(metric_data, datas,  
                                                  rest_filtered=True, d=0.5, beats_indexes=off_beats)
    #interleaved
    results['1st♪♪ inter BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_interleaved_p1)
    results['2nd♪♪ inter BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_interleaved_p2)
    #no interleaved
    results['1st♪♪ NO inter BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_no_interleaved_p1)
    results['2nd♪♪ NO inter BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_no_interleaved_p2)
    ##16th note : 
    results['1st♬♬ BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.25, beats_indexes=sixteenth_p1_indexes)
    results['2nd♬♬ BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.25, beats_indexes=sixteenth_p2_indexes)
    results['3rd♬♬ BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.25, beats_indexes=sixteenth_p3_indexes)
    results['4th♬♬ BM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.25, beats_indexes=sixteenth_p4_indexes)
    
    results['1st♪♪♪ TM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_ternary_p1_indexes)
    results['2nd♪♪♪ TM']=get_metric_of_selected_elements(metric_data, datas, 
                                                       rest_filtered=True, d=0.5, beats_indexes=eight_ternary_p2_indexes)
    results['3rd♪♪♪ TM']=get_metric_of_selected_elements(metric_data, datas, 
                                                      rest_filtered=True, d=0.5, beats_indexes=eight_ternary_p3_indexes)

    #results['1st♬♬x binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                      select_voice='x', d=0.25, beats_indexes=sixteenth_p1_indexes)
    #results['2nd♬♬x binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='x', d=0.25, beats_indexes=sixteenth_p2_indexes)
    #results['3rd♬♬x binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='x', d=0.25, beats_indexes=sixteenth_p3_indexes)
    #results['4th♬♬x binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='x', d=0.25, beats_indexes=sixteenth_p4_indexes)
    #results['1st♬♬S binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='S', d=0.25, beats_indexes=sixteenth_p1_indexes)
    #results['2nd♬♬S binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='S', d=0.25, beats_indexes=sixteenth_p2_indexes)
    #results['3rd♬♬S binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='S', d=0.25, beats_indexes=sixteenth_p3_indexes) 
    #results['4th♬♬S binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='S', d=0.25, beats_indexes=sixteenth_p4_indexes)  
    #results['1st♬♬Bb binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='Bb', d=0.25, beats_indexes=sixteenth_p1_indexes)
    #results['2nd♬♬Bb binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='Bb', d=0.25,beats_indexes=sixteenth_p2_indexes)
    #results['3rd♬♬Bb binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='Bb', d=0.25,beats_indexes=sixteenth_p3_indexes)   
    #results['4th♬♬Bb binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='Bb', d=0.25, beats_indexes=sixteenth_p4_indexes)  
    #results['1st♬♬b binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='bs', d=0.25, beats_indexes=sixteenth_p1_indexes) 
    #results['2nd♬♬b binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='bs', d=0.25,beats_indexes=sixteenth_p2_indexes)
    #results['3rd♬♬b binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                   select_voice='bs', d=0.25,beats_indexes=sixteenth_p3_indexes)
    #results['4th♬♬b binary']=get_metric_of_selected_elements(metric_data, datas, 
    #                                                  select_voice='bs', d=0.25,beats_indexes=sixteenth_p4_indexes)
    return results


def timings(metric: str, performer: str=None, metric_data: list[float]=None, 
                   datas: list=None)->dict[str:dict[str:list]]:
    """_summary_
    
    Args:
        - metric : ioiratios, deltaioi, deltaonsets
        - performer : name of a performer (if None : all performers)
        - metric_data : ioi_ratios or deltasioi per measure or deltasonsets per measure
        - datas

    Returns:
        _description_
    """
    performers_res=dict()
    # one specific performer
    if performer!=None:
        results=get_metric_results(metric_data, datas)
        performers_res[performer] = dict()
        for r in results:
            performers_res[performer][r]=results[r]
        return performers_res
    else :# all performers
        res = get_all_perfs(metric) 
        for p in res.keys():
            performers_res[p]=dict()
            results=get_metric_results(res[p][metric], res[p]['data'])
            for r in results:
                performers_res[p][r]=results[r]
        return performers_res



#####################################
#stats
######################################

def produce_stat(tab)->tuple[float]:
    """_summary_

    Args:
        tab: _description_

    Returns:
        tulNumber of elements, mean, 1st-2nd and 3rd quartile, minimum, maximum, standard deviation 
    """
    mean_tab = mean(tab) if len(tab)>0 else 0
    maxi= max(tab) if len(tab)!=0 else 0
    mini = min(tab) if len(tab)!=0 else 0
    q1, q2, q3 = quantiles(tab,n=4) if len(tab)>=2 else [0,0,0] # Statistics Error raised if less than 2 values
    n = len(tab)
    stdev = pstdev(tab) if len(tab)>0 else 0
    return n, mean_tab, q1, q2, q3, mini, maxi, stdev


def results_to_stats(results)->dict:
    """_summary_

    Returns:
        dico format
        d= {key : [n_elements, mean, q1, q2, q3, mini, maxi, stdev]}
    """
    stats=dict()
    for k in results:
        stats[k]=produce_stat(results[k])
    return stats