import requests
import time
import math

# check 'repeat' times the duration for request/response to specific url (url2check)
# return array with measured duration of request/response to url
def timeit(url2check, measurements, repeat=1):
    tt = []
    for _ in range(repeat):
        start = time.time()
        r = requests.get(url2check, allow_redirects=True)
        end = time.time()
        tt.append(end - start)
        measurements.append(end - start)
    return tt

# return length of password or -1 if length yet unknown
def checkIndex(checks, measurements, deltas, threshold=1):
    if len(checks) > 1:
        std = standardDeviation(measurements)
        lastMeasure=checks[-1]
        previousMesure = checks[-2]
        deltas.append(abs(lastMeasure -previousMesure))
        #print('Gap : '+ str(deltas[-1])+ ' ,std:'+str(std))
        #number should be replaced with STD
        if abs(lastMeasure -previousMesure)>std*threshold:
            return len(checks)-1
    return -1

# get key by value from dictionary
def get_key(dict, val):
    for key, value in dict.items():
         if val == value:
             return key
    return "key doesn't exist"

# claculate the mean value for numbers in values array
def mean(values):
    sum = 0.0
    for a in values:
        sum +=a
    return sum/len(values)

# calculate the standard deviation for numbers in 'values' array
def standardDeviation(values):
    tempSum = 0
    mean1 = mean(values)
    for a in values:
        tempSum += math.pow((a-mean1), 2)
    std = math.sqrt(tempSum/len(values))
    #print('mean:' + str(mean1)+', std:'+str(std))
    return std
