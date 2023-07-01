import numpy as np 

def max_error(y_true, y_pred):
  error = y_true - y_pred
  #return error[np.argmax(np.abs(error))]
  return np.max(np.abs(error))

def mean_difference(y_true, y_pred):
  return np.mean(y_pred - y_true) 