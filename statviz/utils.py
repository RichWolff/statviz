import numpy as np

def get_ci_intervals(a,ci=[.5,99.5,2.5,97.5]):
    confidenceIntervals = np.percentile(a,ci)
    results = {k:v for k,v in zip(ci,confidenceIntervals)}
    return results
