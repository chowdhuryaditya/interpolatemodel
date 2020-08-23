import numpy as np
import matplotlib.pyplot as plt
from __casac__ import *
from scipy.interpolate import interp1d
from taskinit import casalog
def attachms(vis,nomodify,tblock):
	msobj=ms.ms()
	msobj.open(vis,nomodify=nomodify)
	msobj.iterinit(interval=tblock,adddefaultsortcolumns=False)
	endflag=msobj.iterorigin()
	return msobj,endflag


def interpmodel(sourcems,destms,kind='linear'):
	casalog.post("Interpolation model from %s to %s"%(sourcems,destms))
	tbobj=table.table()
	tbobj.open(sourcems+'/SPECTRAL_WINDOW')
	freq=tbobj.getcol('CHAN_FREQ')[:,0]
	tbobj.close()
	tbobj.open(destms+'/SPECTRAL_WINDOW')
	freq_new=tbobj.getcol('CHAN_FREQ')[:,0]
	tbobj.close()
	casalog.post("Number of channels in source ms: %d ; channel width :%f MHz"%(len(freq),(freq[1]-freq[0])/1e6))
	casalog.post("Number of channels in destination ms: %d ; channel width :%f MHz"%(len(freq_new),(freq_new[1]-freq_new[0])/1e6))
	tblock=300
	msfrom,endflag=attachms(sourcems,nomodify=True,tblock=tblock)
	msto,endflag=attachms(destms,nomodify=False,tblock=tblock)
	while(endflag):
		scan=msfrom.getdata(['SCAN_NUMBER'])['scan_number']
		casalog.post("Interpolating scan(s): %s"%np.array2string(np.unique(scan)))
		modelfrom=msfrom.getdata(['MODEL_DATA','FLAG_ROW']) 
		modelto=msto.getdata(['MODEL_DATA']) 

		for ipol in range(0,modelfrom['model_data'].shape[0]):
			for irow in range(0,modelfrom['model_data'].shape[2]):
				modelto['model_data'][ipol,:,irow]= interp1d(freq,modelfrom['model_data'][ipol,:,irow],kind=kind,fill_value='extrapolate',bounds_error=False)(freq_new)

		msto.putdata(modelto)
		endflagto=msto.iternext()
		endflagfrm=msfrom.iternext()
		endflag=np.logical_and(endflagto,endflagfrm)
		if(not endflag and (endflagfrm and endflagto)):
			print("ERROR! Mismatch in size")


def interpolatemodel(visfrom='',visto='',kind='linear'):
	interpmodel(visfrom,visto,kind)
	return None
