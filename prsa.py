# Author: Marciniak Konrad
# https://github.com/finem4n/python-PRSA

# This code is based on:
# Bauer, A., Kantelhardt, J.W., Barthel, P., Schneider, R., Mäkikallio, T., Ulm, K., Hnatkova, K., Schömig, A., Huikuri, H., Bunde, A. and Malik, M., 2006. Deceleration capacity of heart rate as a predictor of mortality after myocardial infarction: cohort study. The lancet, 367(9523), pp.1674-1681.
# Bauer, A., Kantelhardt, J.W., Bunde, A., Barthel, P., Schneider, R., Malik, M. and Schmidt, G., 2006. Phase-rectified signal averaging detects quasi-periodicities in non-stationary data. Physica A: Statistical Mechanics and its Applications, 364, pp.423-434.

import numpy as np

def define_anchors(RRi, L: int, T: int = 1, DC_AC: str = 'DC'):
    """ Returns list of anchors' indexes.

    Keyword arguments:
    RRi     -- array containing R-R intervals
    L       -- size of segments
    T       -- number of values of the time series
    DC_AC   -- 'DC' for deceleration, 'AC' for acceleration
    """

    anchors_indexes = []

    INDEX_MIN = 0
    INDEX_MAX = len(RRi)-1
    
    if L <= T:
        print("L must be longer than T")
        return

    elif T<=0 or not isinstance(T,int) or L<=0 or not isinstance(L,int):
        print("L and T must be positive integers")
        return

    if T == 1:
        for i in range(INDEX_MAX):
            if abs(i+1 - INDEX_MIN) >= L and abs(i+1 - INDEX_MAX) >= L:

                if DC_AC == 'DC' and (RRi[i] < RRi[i+1]):
                    anchors_indexes.append(i+1)

                elif DC_AC == 'AC' and (RRi[i] > RRi[i+1]): 
                    anchors_indexes.append(i+1)

    elif T > 1:
        for i in range(INDEX_MAX):
            if abs(i+1 - INDEX_MIN) >= L and abs(i+1 - INDEX_MAX) >= L:

                if DC_AC == 'DC' and sum(RRi[i+1-T:i+1])/T < sum(RRi[i+1:i+1+T])/T:
                    anchors_indexes.append(i+1)

                if DC_AC == 'AC' and sum(RRi[i+1-T:i+1])/T > sum(RRi[i+1:i+1+T])/T:
                    anchors_indexes.append(i+1)
    
    return anchors_indexes

def define_segments(RRi, anchors_indexes, L: int):
    segments = []

    for i in anchors_indexes:
        tmp_segment = RRi[i-L:i+L]
        segments.append(tmp_segment)

    return segments

def signal_averaging(segments): 
    """Apply phase rectification and signal averaging."""

    averaged_segments = np.mean(segments, axis=0)

    return averaged_segments

def quantification(averaged_segments):
    i0 = len(averaged_segments)//2 + 1

    x0 = averaged_segments[i0]
    x1 = averaged_segments[i0+1]
    x_1 = averaged_segments[i0-1]
    x_2 = averaged_segments[i0-2]

    DC_AC = (x0 + x1 - x_1 - x_2)/4

    return DC_AC


def eval_ACDC(RRi, L: int, T: int)-> tuple[float, float]:
    """ Returns both DC and AC values. Units as in RRi """

    anchors_DC_indexes = define_anchors(RRi, L, T, 'DC')
    segments_DC = define_segments(RRi, anchors_DC_indexes, L)
    averaged_segments_DC = signal_averaging(segments_DC)
    DC = quantification(averaged_segments_DC)

    anchors_AC_indexes = define_anchors(RRi, L, T, 'AC')
    segments_AC = define_segments(RRi, anchors_AC_indexes, L)
    averaged_segments_AC = signal_averaging(segments_AC)
    AC = quantification(averaged_segments_AC)

    return DC, AC 
