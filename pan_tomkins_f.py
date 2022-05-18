import numpy as np
import pandas as pd
import math
import sys

# TODO: hacer que el timestamp se pase como parametros desde la funcion que inicializa el analisis
time_stamp = []
fs = 360


def iniciar(ecg, signal_len):
  for i in range(0,signal_len):
    time_stamp.append(i)
  print(len(time_stamp))
  arr = np.array(ecg)
  QRS_detector = Pan_Tompkins_QRS()
  integration_signal, band_pass_signal, derivative_signal, square_signal  = QRS_detector.solve(arr.copy())

  fs = 360
    

  r_peaks = detect_peaks(arr, fs, integration_signal, band_pass_signal)
  heart_beat = np.average(np.diff(r_peaks))/ fs
  return heart_beat

class Pan_Tompkins_QRS():

  def low_pass_filter(self, signal):
    low_pass_signal = signal.copy()
    for time in time_stamp:
      curr = signal[time] 

      if (time >= 1):
        curr += 2*low_pass_signal[time-1]

      if (time >= 2):
        curr -= low_pass_signal[time-2]

      if (time >= 6):
        curr -= 2*signal[time-6]
      
      if (time >= 12):
        curr += signal[time-12]

      low_pass_signal[time] = curr
    low_pass_signal = low_pass_signal/ max(abs(low_pass_signal))
    return low_pass_signal

  def high_pass_filter(self, signal):

    high_pass_signal = signal.copy()

    for time in time_stamp:
      curr = -1*signal[time]

      if (time >= 16):
        curr += 32*signal[time-16]

      if (time >= 1):
        curr -= high_pass_signal[time-1]

      if (time >= 32):
        curr += signal[time-32]

      high_pass_signal[time] = curr 
    high_pass_signal = high_pass_signal/max(abs(high_pass_signal))
    return high_pass_signal

  
  def band_pass_filter(self,signal):
    low_pass_signal = self.low_pass_filter(signal)
    band_pass_signal = self.high_pass_filter(low_pass_signal)

    return band_pass_signal    

  
  def derivative(self,signal):
    T = 1/fs
    derivative_signal = signal.copy()

    for time in time_stamp:
      curr = 0

      if (time >= 2):
        curr -= signal[time-2]

      if (time >= 1):
        curr -= 2*signal[time-1]
        
      if (time < len(time_stamp)-1):
        curr += 2*signal[time+1]

      if (time < len(time_stamp)-2):
        curr += signal[time+2]
      derivative_signal[time] = (curr/(8*T))
    
    return derivative_signal

  def squaring(self,signal):
    return np.square(signal)

  def moving_window_integration(self,signal):
    WINDOW_SIZE = 0.15*fs
    moving_window_signal = signal.copy()
    for time in time_stamp:
      index = 0
      curr = 0
      while (index < WINDOW_SIZE):
        if (time < index):
          break
        curr += signal[time-index]
        index += 1

      moving_window_signal[time] = curr/index
    return moving_window_signal


  def solve(self,signal):

    band_pass_signal = self.band_pass_filter(signal.copy())
    derivative_signal = self.derivative(band_pass_signal.copy())
    square_signal = self.squaring(derivative_signal.copy())
    moving_window_avg_signal = self.moving_window_integration(square_signal.copy())

    return moving_window_avg_signal,band_pass_signal, derivative_signal, square_signal

def detect_peaks(ecg_signal, fs, integration_signal, band_pass_signal): 
    

    possible_peaks = []
    signal_peaks = []
    r_peaks = []
    
    SPKI = 0
    
    SPKF = 0
    
    NPKI = 0
    
    NPKF = 0
    rr_avg_one = []
    
    THRESHOLDI1 = 0
    
    THRESHOLDF1 = 0
    rr_avg_two = []
    
    THRESHOLDI2 = 0
    
    THRESHOLDF2 = 0
    
    is_T_found = 0
    
    window = round(0.15 * fs)            

    
    FM_peaks = []
    
    integration_signal_smooth = np.convolve(integration_signal, np.ones((20,)) / 20, mode = 'same')    
    localDiff = np.diff(integration_signal_smooth)
    
    

    for i in range(1,len(localDiff)):
        if i-1 > 2*fs and localDiff[i-1] > 0 and localDiff[i] < 0 :
            FM_peaks.append(i-1)           

    
    for index in range(len(FM_peaks)):

        
        current_peak = FM_peaks[index]
        left_limit = max(current_peak-window, 0) 
        right_limit = min(current_peak+window+1, len(band_pass_signal))
        max_index = -1
        max_value = -sys.maxsize
        for i in range(left_limit, right_limit):
            if(band_pass_signal[i] > max_value):
                max_value = band_pass_signal[i]
                max_index = i
        if (max_index != -1):
            possible_peaks.append(max_index)

        if (index == 0 or index > len(possible_peaks)):
          
          if (integration_signal[current_peak] >= THRESHOLDI1): 
              SPKI = 0.125 * integration_signal[current_peak]  + 0.875 * SPKI
              if possible_peaks[index] > THRESHOLDF1:                                            
                  SPKF = 0.125 * band_pass_signal[index] + 0.875 * SPKF 
                  signal_peaks.append(possible_peaks[index])                             
              else:
                  NPKF = 0.125 * band_pass_signal[index] + 0.875 * NPKF                                    
              
          elif ( (integration_signal[current_peak] > THRESHOLDI2 and integration_signal[current_peak] < THRESHOLDI1) or (integration_signal[current_peak] < THRESHOLDI2)):
              NPKI = 0.125 * integration_signal[current_peak]  + 0.875 * NPKI  
              NPKF = 0.125 * band_pass_signal[index] + 0.875 * NPKF

        else:
            RRAVERAGE1 = np.diff(FM_peaks[max(0,index-8):index + 1]) / fs
            rr_one_mean = np.mean(RRAVERAGE1)
            rr_avg_one.append(rr_one_mean) 
            limit_factor = rr_one_mean
              
            if (index >= 8):
                
                for RR in RRAVERAGE1:
                    if RR > RR_LOW_LIMIT and RR < RR_HIGH_LIMIT:                              
                        rr_avg_two.append(RR)
                        if (len(rr_avg_two) == 9):
                          rr_avg_two.pop(0)     
                          limit_factor = np.mean(rr_avg_two)
            
            if (len(rr_avg_two) == 8 or index < 8):
                RR_LOW_LIMIT = 0.92 * limit_factor        
                RR_HIGH_LIMIT = 1.16 * limit_factor
                RR_MISSED_LIMIT = 1.66 * limit_factor

            
            if rr_avg_one[-1] < RR_LOW_LIMIT or rr_avg_one[-1] > RR_MISSED_LIMIT: 
                THRESHOLDI1 = THRESHOLDI1/2
                THRESHOLDF1 = THRESHOLDF1/2
               
            
            curr_rr_interval = RRAVERAGE1[-1]
            search_back_window = round(curr_rr_interval * fs)
            if curr_rr_interval > RR_MISSED_LIMIT:
                left_limit = current_peak - search_back_window +1
                right_limit = current_peak + 1
                search_back_max_index = -1 
                max_value =  -sys.maxsize
                
                for i in range(left_limit, right_limit):
                  if (integration_signal[i] > THRESHOLDI1 and integration_signal[i] > max_value ):
                    max_value = integration_signal[i]
                    search_back_max_index = i
              
                if (search_back_max_index != -1):   
                    SPKI = 0.25 * integration_signal[search_back_max_index] + 0.75 * SPKI                         
                    THRESHOLDI1 = NPKI + 0.25 * (SPKI - NPKI)
                    THRESHOLDI2 = 0.5 * THRESHOLDI1               
                    
                    left_limit = search_back_max_index - round(0.15 * fs)
                    right_limit = min(len(band_pass_signal), search_back_max_index)

                    search_back_max_index2 = -1 
                    max_value =  -sys.maxsize
                    
                    for i in range(left_limit, right_limit):
                      if (band_pass_signal[i] > THRESHOLDF1 and band_pass_signal[i] > max_value ):
                        max_value = band_pass_signal[i]
                        search_back_max_index2 = i

                    
                    if band_pass_signal[search_back_max_index2] > THRESHOLDF2: 
                        SPKF = 0.25 * band_pass_signal[search_back_max_index2] + 0.75 * SPKF                            
                        THRESHOLDF1 = NPKF + 0.25 * (SPKF - NPKF)
                        THRESHOLDF2 = 0.5 * THRESHOLDF1                            
                        signal_peaks.append(search_back_max_index2)                                                 
    
            
            if (integration_signal[current_peak] >= THRESHOLDI1): 
                if (curr_rr_interval > 0.20 and curr_rr_interval < 0.36 and index > 0): 
                    
                    current_slope = max(np.diff(integration_signal[current_peak - round(fs * 0.075):current_peak + 1]))
                    
                    previous_slope = max(np.diff(integration_signal[FM_peaks[index - 1] - round(fs * 0.075): FM_peaks[index - 1] + 1]))
                    if (current_slope < 0.5 * previous_slope): 
                        NPKI = 0.125 * integration_signal[current_peak] + 0.875 * NPKI                                            
                        is_T_found = 1                              
                
                if (not is_T_found):
                    SPKI = 0.125 * integration_signal[current_peak]  + 0.875 * SPKI
                    
                    if possible_peaks[index] > THRESHOLDF1:                                            
                        SPKF = 0.125 * band_pass_signal[index] + 0.875 * SPKF 
                        signal_peaks.append(possible_peaks[index])                             
                    else:
                        NPKF = 0.125 * band_pass_signal[index] + 0.875 * NPKF                   
                                        
            elif ((integration_signal[current_peak] > THRESHOLDI1 and integration_signal[current_peak] < THRESHOLDI2) or (integration_signal[current_peak] < THRESHOLDI1)):
                NPKI = 0.125 * integration_signal[current_peak]  + 0.875 * NPKI  
                NPKF = 0.125 * band_pass_signal[index] + 0.875 * NPKF
       
        THRESHOLDI1 = NPKI + 0.25 * (SPKI - NPKI)
        THRESHOLDF1 = NPKF + 0.25 * (SPKF - NPKF)
        THRESHOLDI2 = 0.5 * THRESHOLDI1 
        THRESHOLDF2 = 0.5 * THRESHOLDF1
        is_T_found = 0  

    
    for i in np.unique(signal_peaks):
        i = int(i)
        window = round(0.2 * fs)
        left_limit = i-window
        right_limit = min(i+window+1, len(ecg_signal))
        max_value = -sys.maxsize
        max_index = -1
        for i in range(left_limit, right_limit):
            if (ecg_signal[i] > max_value):
                max_value = ecg_signal[i]
                max_index = i

        r_peaks.append(max_index)
        
    return r_peaks
