from pyatc import pyatc
import pyedflib
import os
import numpy as np
import pandas as pd
from biosppy.signals import ecg
import matplotlib.pyplot as plt
import shutil

plt.style.use('dark_background')

path = './'
tmp = path+"tmp/"

if os.path.exists(tmp):
    shutil.rmtree(tmp)
os.makedirs(tmp)

atc_files = [f for f in os.listdir(path) if '.atc' in f]
for f in atc_files:
    pyatc.PyATC.read_file(f).write_edf_to_file(tmp+f+".edf")

files = [f for f in os.listdir(tmp) if '.edf' in f]
df = pd.DataFrame()
count = 1
for f in files:
    f = pyedflib.EdfReader(tmp + f)
    n = f.signals_in_file
    signal_labels = f.getSignalLabels()
    sigbufs = np.zeros((n, f.getNSamples()[0]))
    for i in np.arange(n):
        sigbufs[i, :] = f.readSignal(i)
    out = ecg.ecg(signal=sigbufs[0], show=False)
    rpeaks = out[2]
    templates = out[4]
    for t in templates:
        df[str(count)] = t
        count = count + 1

df['mean_value'] = df.mean(axis = 1)
df['std'] = df.std(axis = 1)

drops = []
cols = [c for c in df.columns if c not in ['mean_value', 'std']]
n = 3
for c in cols:
    if (df[c] <= (df['mean_value'] - n * df['std'])).sum() > 0 or (df[c] >= (df['mean_value'] + n * df['std'])).sum() > 0:
        drops.append(c)
df.drop(drops, axis = 1, inplace = True)

plt.close('all')
cols = [c for c in df.columns if c not in ['mean_value', 'std']]
#Change colormap here for different results
colors = plt.cm.Reds(np.linspace(0, 1, len(cols)))

plt.figure(figsize = (30, 20), frameon = False)
for i in range(len(cols)):
    plt.plot(range(len(df)), df[cols[i]], color = colors[i], lw = 1)
plt.xlim((50, 350))
plt.ylim((-0.4, 0.6))
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(path + 'plot.png') #, pad_inches = 0, bbox_inches = 'tight')

shutil.rmtree(tmp)
