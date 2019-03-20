import pylab as plt, numpy as np
fig,ax = plt.subplots(1,3,figsize=(20,5))

for sn in range(1,25):
    d = np.genfromtxt('./scans/scan_{}.txt'.format(sn),skip_header=2,delimiter=',')
    #d = np.genfromtxt('scan_{}.txt'.format(sn),skip_header=2,delimiter=',')
    re = d[:,1]*np.cos(d[:,2]*np.pi*2./360.)
    im = d[:,1]*np.sin(d[:,2]*np.pi*2./360.)
    ax[0].loglog(d[:,0],d[:,1])
    ax[1].semilogx(d[:,0],d[:,2])
    ax[2].plot(re,-im,'o',label=str(sn))

plt.legend()
plt.show()