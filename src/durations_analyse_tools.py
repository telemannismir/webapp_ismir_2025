#!/usr/bin/env python3
from src.data import *
from functools import reduce
from fractions import Fraction
from math import modf

####################
# TIME SIGNATURES
####################
BINARY_TS = ['2/4','3/4','4/4']
TERNARY_TS = ['3/8','6/8','9/8','12/8']
COMPOUND_TS= ['3/2','6/4']

####################
# functions
####################

def get_movement_time_duration(data, movement)-> float:
    """_summary_

    Args:
        data: _description_
        movement: _description_

    Returns:
        time duration of a movement in s
    """
    mov = get_data_movement(data, movement)
    if len(mov)==0:
        return 0
    else:
        res = float(mov[-1]['onset']) + float(mov[-1]['ioi']) - float(mov[0]['onset'])
        return round(res/1000, 2)


def movement_durations_in_all_perf(fantasia: int, movement:int)-> list[float]:
    """_summary_

    Args:
        fantasia: fantasia number
        movement: movement number
    Returns:
        _description_
    """
    res=[]
    for performer, tuning in PERFORMERS_AND_TUNING:
        data = get_all_data(performer, fantasia)
        res.append(get_movement_time_duration(data, str(movement)))
    return res


def fantasias_durations_in_all_perf()-> dict[str:dict[int:float]]:
    """_summary_

    Returns:
        dictionnary keys : performer name
                    value : dictionnary with keys fantasia number 
                                            and value time_duration
    """
    res={p:dict() for p,t in PERFORMERS_AND_TUNING}
    for performer, tuning in PERFORMERS_AND_TUNING:
        res_performer={i:[] for i in range(1,13)}
        for fantasia in range(1, 13):
            acc = 0
            data = get_all_data(performer, fantasia)
            for i in range(1, len(MOVEMENTS[fantasia])+1):
                acc+=get_movement_time_duration(data, str(i))
            res_performer[fantasia]=round(acc,2)
        res[performer]=res_performer
    return res


def get_corpus_duration_in_all_perf():
    durations_dict = fantasias_durations_in_all_perf()
    res={performer:0 for performer in durations_dict}
    for performer in durations_dict:
        acc=0
        for v in durations_dict[performer].values():
            acc+= v
        res[performer]=acc
    return res


def get_metronomic_ioi(data: list[dict])->list[float]:
    """Produce sequence of predicted metronomic IOI 
    in ms according to the real total timeduration of this sequence

    Args:
        data: data corresponding to a performer and a fantasia
            and a specific range of measures (or movement)
    
    Returns:
        sequence of metronomic IOI in ms
    """
    #real iois based on the onset in ms
    iois=[float(e['ioi']) for e in data]
    # quarter note durations
    durations=[float(e['duration']) for e in data]   
    # total duration in quarter note equivalent
    total_durations_in_quarter_note = reduce(lambda acc,d : acc+d, durations)
    # total movement duration in ms
    seq_time_duration=reduce(lambda acc,d : acc+d, iois)
    # theorical iois 
    res= []
    for i in range(len(data)):
       res.append(durations[i]*seq_time_duration/total_durations_in_quarter_note)
    return res


def get_ioi_ratios(ioi: list[float], metronomic_ioi: list[float])->list[float]:
    """Produce ioi ratios corresponding to the quotient 
    of the real ioi by the metronomic one (predicted)

    Args:
        ioi: sequence of real ioi  in ms
        metronomic_ioi: sequence of predicted metronomic ioi in ms

    Returns:
        sequence of ioi_ratio : 1 is 100%, 1.1 110, 0,9 : 90 etc..
    """
    ratios=[]
    for i in range(len(ioi)):
        deviation_in_percent = ioi[i]*100/metronomic_ioi[i] - 100
        ratios.append(1+deviation_in_percent/100)
    return ratios

###########
# NEW
###############
def get_delta_ioi_per_measure(iois: list[float], metronomic_ioi: list[float])->list[float]:
    """_summary_

    Args:
        iois: _description_
        metronomic_ioi: _description_

    Returns:
        (ioi-metronomic_ioi)/measure_time_duration
    """
    # total seq duration in ms
    measure_time_duration=reduce(lambda acc,d : acc+d, iois)
    # delta ioi per measure 
    res=[]
    for i in range(len(iois)):
        res.append((iois[i]-metronomic_ioi[i])/measure_time_duration)
    return res


def get_delta_onset_per_measure(real_onsets: list[float], metronomic_onsets: list[float], iois: list[float])->list[float]:
    """_summary_

    Args:
        real_onsets: _description_
        metronomic_onsets: _description_
        measure_duration: _description_

    Returns:
        _description_
    """
    # total seq duration in ms
    measure_time_duration=reduce(lambda acc,d : acc+d, iois)
    res=[]
    for i in range(len(real_onsets)):
        #print(real_onsets[i]- metronomic_onsets[i])
        res.append((real_onsets[i]- metronomic_onsets[i])/measure_time_duration)
    return res

 
##########################################
# positions in measures & beats
##########################################
def measure_duration_in_quarter_notes(event: dict[str:str])-> float:
    """Duration in quarter notes of the measure containing the event

    Args:
        - event : note or rest (element of data)

    Returns:
        Measure duration in quarter notes
    """
    a,b = event['time_signature'].split('/')
    return 4*int(a)/int(b)


def beats_number_in_a_measure(element: dict[str:str])-> float:
    a,b = element['time_signature'].split('/')
    return int(a)


def filtered_beats_indexes(data: list[dict[str:str]], 
                           measures_positions: list[float],
                           beats:str)->list[int]:
    """_summary_

    Args:
        data : data like data movement (if needed)
        measures_positions
        beats: 'first' if only 1st beats, 'on' for only notes on a beat, 'off' for notes off beats

    Returns:
        sequence of indexes
    """
    if beats=='first':
        indexes = strongbeats_index(measures_positions)
    elif beats == 'on':
        indexes = beat_indexes(data, measures_positions)
    elif beats=='off':
        on = beat_indexes(data, measures_positions)
        indexes = [i for i in range(len(data)) if i not in on]
        assert(len(indexes)+len(on)==len(data))
    return indexes


def get_positions_in_measures_fractions(data: list[dict[str:str]])->list[float]:
    """Sequence of (floating measure numbers (duration add as a fraction of the measure number)
    for each note 

    Args:
        data

    Returns:
        sequences of float
    """
    res = []
    durations = [float(e['duration']) for e in data]
    measure_duration = measure_duration_in_quarter_notes(data[0])
    current_m = None
    for i in range(len(data)):
        measure = float(data[i]['measure'])
        if measure != current_m:
            res.append(float(measure))
            current_m = measure
            measure_duration = measure_duration_in_quarter_notes(data[i])
        else:
            res.append(res[i-1] + durations[i-1]/measure_duration)
    #print(res) # only for tests
    return res


def strongbeats_index(measures_positions: list[float])->list[int]:
    """_summary_

    Args:
        measures_positions: _description_

    Returns:
        _description_
    """
    return [i for i in range(len(measures_positions)) if Fraction(measures_positions[i]).denominator == 1]


def beat_indexes(data: list[dict[str:str]], measures_positions: list[float])->list[int]:
    """_summary_

    Args:
        data: _description_
        measures_positions: _description_

    Returns:
        index of beats in the data sequence
    """
    beats_number = [beats_number_in_a_measure(d) for d in data]
    dico_denom = {2:(1,2),
                  3:(1,3),
                  4:(1,2,4),
                  6:(1,2),
                  9:(1,3),
                  12:(1,2,4)}
    denom=[dico_denom[b] for b in beats_number]
    return [i for i in range(len(data)) if Fraction(measures_positions[i]).limit_denominator(100).denominator in denom[i]]


def get_binary_sixteenth_indexes(data: list[dict[str:str]], measures_positions: list[float], position: int)-> list[int]:
    """indexes in sequence of data of sixteenth notes of a group of 4 in binary meter

    Args:
        data: _description_
        measures_positions: _description_
        position: 1,2,3 or 4

    Returns:
        _description_
    """
    positions_fractions=[Fraction(modf(m)[0]).limit_denominator(100) for m in measures_positions]
    positions_numdem=[str(frac.numerator)+'/'+str(frac.denominator) for frac in positions_fractions]
    denom=[str(frac.denominator) for frac in positions_fractions]
    indexes=[]
    
    for i in range(len(data)):
        ts=data[i]['time_signature']
        if data[i]['voice']!= '.':
            if ts == '2/4':    
                if (position == 1 and denom[i] in ['1', '2'] and i<= (len(data)-4)
                    and data[i+1]['measure']==data[i+2]['measure']==data[i+3]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']==data[i+3]['duration']=="0.25"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.' and data[i+3]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/8', '5/8'] and i< (len(data)-3)
                    and data[i-1]['measure']==data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']==data[i+2]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.' and data[i+2]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] in ['1/4', '3/4'] and i<= (len(data)-2)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i+1]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i+1]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 4 and positions_numdem[i] in ['3/8', '7/8'] and i<= (len(data)-1)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i-3]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i-3]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i-3]['voice']!= '.')  :
                        indexes.append(i)
            elif ts == '3/4':
                if (position == 1 and denom[i] in ['1', '3'] and i<= (len(data)-4)
                    and data[i+1]['measure']==data[i+2]['measure']==data[i+3]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']==data[i+3]['duration']=="0.25"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.' and data[i+3]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/12', '5/12', '3/4'] and i<= (len(data)-3)
                    and data[i-1]['measure']==data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']==data[i+2]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.' and data[i+2]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] in ['1/6', '1/2', '5/6'] and i<= (len(data)-2)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i+1]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i+1]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 4 and positions_numdem[i] in ['1/4', '7/12', '11/12'] and i<= (len(data)-1)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i-3]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i-3]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i-3]['voice']!= '.') :
                        indexes.append(i)    
            elif ts == '4/4':
                if (position == 1 and denom[i] in ['1', '2', '4'] and i<= (len(data)-4)
                    and data[i+1]['measure']==data[i+2]['measure']==data[i+3]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']==data[i+3]['duration']=="0.25"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.' and data[i+3]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/16', '5/16', '9/16', '13/16'] and i<= (len(data)-3)
                    and data[i-1]['measure']==data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']==data[i+2]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.' and data[i+2]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] in ['1/8', '3/8', '5/8', '7/8'] and i<= (len(data)-2)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i+1]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i+1]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 4 and positions_numdem[i] in ['3/16', '7/16', '11/16', '15/16'] and i<= (len(data)-1)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i-3]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']==data[i-3]['duration']=="0.25"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.' and data[i-3]['voice']!= '.')  :
                        indexes.append(i)
    return indexes


def get_ternary_eight_indexes(data: list[dict[str:str]], measures_positions: list[float], position: int)-> list[int]:
    """_summary_

    Args:
        data: _description_
        measures_positions: _description_
        position: 2 or 3

    Returns:
        _description_
    """
    positions_fractions=[Fraction(modf(m)[0]).limit_denominator(100) for m in measures_positions]
    positions_numdem=[str(frac.numerator)+'/'+str(frac.denominator) for frac in positions_fractions]
    denom=[str(frac.denominator) for frac in positions_fractions] 
    indexes=[]
    
    for i in range(len(data)):
        ts=data[i]['time_signature']
        if data[i]['voice']!= '.' :
            if ts == '3/8':
                if  (position == 1 and denom[i]=='1' and i<= (len(data)-3)
                     and data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']=="0.5"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] == '1/3' and i<= (len(data)-2)
                     and data[i-1]['measure']==data[i+1]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] == '2/3'and i<= (len(data)-1)
                     and data[i-1]['measure']==data[i-2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.') :
                        indexes.append(i)
            elif ts == '6/8':
                if (position == 1 and denom[i] in ['1', '2'] and i<= (len(data)-3)
                    and data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']=="0.5"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/6', '2/3'] and i<= (len(data)-2)
                      and data[i-1]['measure']==data[i+1]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] in ['1/3', '5/6'] and i<= (len(data)-1)
                    and data[i-1]['measure']==data[i-2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.') :
                        indexes.append(i)  
            elif ts == '9/8':
                if  (position == 1 and denom[i] in ['1', '3'] and i<= (len(data)-3)
                    and data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']=="0.5"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/9', '4/9', '7/9'] and i<= (len(data)-2)
                      and data[i-1]['measure']==data[i+1]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.') or\
                    (position == 3 and positions_numdem[i] in ['2/9', '5/9', '8/9'] and i<= (len(data)-1)
                     and data[i-1]['measure']==data[i-2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.') :
                        indexes.append(i)  
            elif ts == '12/8':
                if  (position == 1 and denom[i] in ['1', '2', '4'] and i<= (len(data)-3)
                     and data[i+1]['measure']==data[i+2]['measure']==data[i]['measure']
                    and data[i+1]['duration']==data[i+2]['duration']=="0.5"
                    and data[i+1]['voice'] != '.' and data[i+2]['voice'] != '.') or\
                    (position == 2 and positions_numdem[i] in ['1/12', '1/3', '7/12', '5/6'] and i<= (len(data)-2)
                      and data[i-1]['measure']==data[i+1]['measure']
                    and data[i-1]['duration']==data[i+1]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i+1]['voice']!= '.')or\
                    (position == 3 and positions_numdem[i] in ['1/6', '5/12', '2/3', '11/12'] and i<= (len(data)-1)
                     and data[i-1]['measure']==data[i-2]['measure']==data[i]['measure']
                    and data[i-1]['duration']==data[i-2]['duration']=="0.5"
                    and data[i-1]['voice']!= '.' and data[i-2]['voice']!= '.') :
                        indexes.append(i) 
    return indexes


def get_binary_eight_interleaved_indexes(data: list[dict[str:str]], measures_positions: list[float], position: int)-> list[int]:
    """indexes in sequence of data of eight notes of a group of 2 in binary meter

    Args:
        data: _description_
        measures_positions: _description_
        position: 1,2,3 or 4

    Returns:
        _description_
    """
    positions_fractions=[Fraction(modf(m)[0]).limit_denominator(100) for m in measures_positions]
    #positions_numdem=[str(frac.numerator)+'/'+str(frac.denominator) for frac in positions_fractions]
    denom=[str(frac.denominator) for frac in positions_fractions]
    indexes=[]
    
    for i in range(len(data)):
        ts=data[i]['time_signature']
        if data[i]['voice']not in 'x.':
            if ts == '2/4':    
                if (position == 1 and denom[i] in ['1', '2'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice'] not in 'x.' and data[i+1]['voice'] != data[i]['voice']) or\
                    (position == 2 and denom[i]=='4'
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice'] not in 'x.' and data[i-1]['voice'] != data[i]['voice']) :
                        indexes.append(i)
            elif ts == '3/4':
                if (position == 1 and denom[i] in ['1', '3'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice'] not in 'x.' and data[i+1]['voice'] != data[i]['voice']) or\
                    (position == 2 and denom[i] in ['2', '6'] 
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice'] not in 'x.' and data[i-1]['voice'] != data[i]['voice']) :
                        indexes.append(i)    
            elif ts == '4/4':
                if (position == 1 and denom[i] in ['1', '2', '4'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice'] not in 'x.' and data[i+1]['voice'] != data[i]['voice']) or\
                    (position == 2 and denom[i] =='8' 
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice'] not in 'x.' and data[i-1]['voice'] != data[i]['voice']) :
                        indexes.append(i)
    return indexes


def get_binary_eight_not_interleaved_indexes(data: list[dict[str:str]], measures_positions: list[float], position: int)-> list[int]:
    """indexes in sequence of data of eight notes of a group of 2 in binary meter

    Args:
        data: _description_
        measures_positions: _description_
        position: 1,2,3 or 4

    Returns:
        _description_
    """
    positions_fractions=[Fraction(modf(m)[0]).limit_denominator(100) for m in measures_positions]
    #positions_numdem=[str(frac.numerator)+'/'+str(frac.denominator) for frac in positions_fractions]
    denom=[str(frac.denominator) for frac in positions_fractions]
    indexes=[]
    
    for i in range(len(data)):
        ts=data[i]['time_signature']
        if data[i]['voice']=='x':
            if ts == '2/4':    
                if (position == 1 and denom[i] in ['1', '2'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice']=='x') or\
                    (position == 2 and denom[i]=='4'
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice']== 'x') :
                        indexes.append(i)
            elif ts == '3/4':
                if (position == 1 and denom[i] in ['1', '3'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice']=='x') or\
                    (position == 2 and denom[i] in ['2', '6'] 
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice']== 'x') :
                        indexes.append(i)    
            elif ts == '4/4':
                if (position == 1 and denom[i] in ['1', '2', '4'] and i< (len(data)-1)
                    and data[i+1]['measure']==data[i]['measure']
                    and data[i+1]['duration']=="0.5"
                    and data[i+1]['voice']=='x') or\
                    (position == 2 and denom[i] =='8' 
                    and data[i-1]['measure']==data[i]['measure']
                    and data[i-1]['duration']=="0.5"
                    and data[i-1]['voice']== 'x') :
                        indexes.append(i)
    return indexes
##########################################
# performances analyse
##########################################

def  get_all_metric_and_data_for_one_performer(performer:str, metric:str, 
                                               f: int=None, fugato=False, movement_name: str=None)->tuple[list,list]:
    """_summary_

    Args:
        performer: name of the performer   
        metric: deltaioi, deltasonsets
        f: number of a fantasia or None for all
        fugato : True if only fugatos movements, False otherwise
        movement_name : None if all type movements

    Returns:
        (metric_data, data) for all fantasias respecting the scale of a measure
    """
    data_all=[]
    metric_all=[]
    if f == None:
        f_start, f_end = 1, 13
    else:
        f_start, f_end = f, f+1
    for fantasia in range(f_start, f_end):
        data = get_all_data(performer, fantasia)
        # filtered grace notes and movements separations (rests not written)
        datafiltered= [d for d in data if float(d['duration'])!=0.0]
        if movement_name!=None:    
            datafiltered=[d for d in datafiltered 
                          if (fantasia in MOVEMENTS_POSITIONS[movement_name] and 
                              int(d['movement']) in MOVEMENTS_POSITIONS[movement_name][fantasia])] 
        if not fugato:
            measures_sequences = MEASURES_BY_PERFORMERS[performer][fantasia]
        else :
            measures_sequences = MEASURES_FUGATOS_BY_PERFORMERS[performer][fantasia]
        for i in range(len(measures_sequences)):
            s,e,r = measures_sequences[i]
            if e==None: 
                e=s
            elif s==e==r==0:
                break
            for m in range(s, e+1):
                measurefiltered = [d for d in datafiltered if (int(d['measure'])== m and int(d['repeated'])== r)]
                if len(measurefiltered)==0:
                    continue
                iois=[float(e['ioi']) for e in measurefiltered]
                metronomic_ioi= get_metronomic_ioi(measurefiltered)
                data_all.extend(measurefiltered)
                if metric == "ioiratios":
                    metric_all.extend(get_ioi_ratios(iois, metronomic_ioi))
                elif metric == "deltaioi":
                    metric_all.extend(get_delta_ioi_per_measure(iois, metronomic_ioi))
                elif metric == "deltaonset":
                    real_onsets = [float(e['onset']) for e in measurefiltered]
                    metronomic_onsets = []
                    acc=real_onsets[0]
                    metronomic_onsets.append(acc)
                    for i in range(1, len(real_onsets)):
                        acc += metronomic_ioi[i-1]
                        metronomic_onsets.append(acc)
                    metric_all.extend(get_delta_onset_per_measure(real_onsets, metronomic_onsets, iois))
    return metric_all, data_all



def get_all_perfs(metric: str)->dict[str:dict[str:list]]:
    """_summary_
    
    Args:
        - metric : ioiratios, deltaioi, deltaonset

    Returns:
        dictionnary with each - key : performer name
                              - value : dictionnary of results
        for the dictionnary of results :
            - keys : 'ioi_ratios' (or 'ioi_deltas' or 'onset_deltas'), 'data'
            - values : respectively list[float] and list[str]
    """
    res= {p:None for p,t in PERFORMERS_AND_TUNING}
    for performer in res.keys():
        metric_all, data_all = get_all_metric_and_data_for_one_performer(performer, metric=metric)
        res[performer]={metric:metric_all, 'data':data_all}
    return res



