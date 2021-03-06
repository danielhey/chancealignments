import numpy as np
from astropy.io import fits as pyfits
from astropy import wcs
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LogNorm
import os

mpl.rc('text', usetex=True)
mpl.rcParams['text.latex.preamble'] = [
      r'\usepackage{helvet}',
      r'\usepackage[EULERGREEK]{sansmath}',
      r'\sansmath'
]

### IMAGE 1: ONE KEPLER PIXEL IMAGE, Q_ ###

quarterlist = []

for i in os.listdir(os.getcwd()):
   if i.endswith("lpd-targ.fits"):
      exec("hdulist_temp = pyfits.open('%s')" % i)
      parameters = hdulist_temp[0].header
      q = parameters['QUARTER']
      quarterlist.append(q)
      hdulist_temp.close()
   else:
      continue

print ' '
repquarter = 18 # placeholder, since there is 0 but there is no 18
while repquarter not in quarterlist:
   while True:
      try:
         repquarter = int(raw_input('--> Which quarter? (0-17) '))
         break
      except ValueError:
         print '--> Please enter an integer'
   if repquarter in quarterlist:
      break
   else:
      print '--> No data for this quarter'
      continue
print ' '

for i in os.listdir(os.getcwd()):
   if i.endswith("lpd-targ.fits"):
      exec("hdulist_temp = pyfits.open('%s')" % i)
      parameters = hdulist_temp[0].header
      q = parameters['QUARTER']
      if repquarter == q:
         exec("hdulist = pyfits.open('%s')" % i)
         parameters = hdulist[0].header
         kic = parameters['KEPLERID']
         channel = parameters['CHANNEL']
         hd2 = hdulist[2].header
         refx = hd2['CRPIX1']
         refy = hd2['CRPIX2']
         refra = hd2['CRVAL1']
         refdec = hd2['CRVAL2']
         break
      else:
         continue
   else:
      continue

if (channel%2) == 0:
   eo = 0
else:
   eo = 1

table = hdulist[1].data
flux = table['FLUX']
#flux_err = table['FLUX_ERR']
time = table['TIME']
hd1 = hdulist[1].header

w = wcs.WCS(hd1, keysel=['binary'])

table2 = hdulist[2].data
hd2 = hdulist[2].header
x = hd2['NAXIS1'] 
y = hd2['NAXIS2']

hdulist.close()

imgflux = np.flipud(flux[0])
if eo == 0:
   imgflux = np.fliplr(imgflux)


### IMAGE 2: UKIRT IMAGE ###

for i in os.listdir(os.getcwd()):
   if i.endswith(".fits"):
      if not i.endswith("llc.fits") and not i.endswith("lpd-targ.fits"):
         exec("hdulist = pyfits.open('%s')" % i)
         break
   else:
      continue

flux2 = hdulist[1].data
parameters = hdulist[1].header
cam = parameters['CAMNUM']

rotby = 360 - 90*cam
rotby /= 90
flux2 = np.rot90(flux2, rotby)


### PLOTTING ###

ref = raw_input('--> Plot the reference pixel on the Kepler image? (y/n) ')
while ref != "y" and ref != "n":
   ref = raw_input('--> Please enter y or n: ')

fig, (kepler, ukirt) = plt.subplots(1, 2) 

exec("fig.suptitle('%d', fontsize=20)" % kic)

left = kepler.imshow(imgflux, cmap='pink')
kepler.set_title('Kepler Aperture')
left.set_interpolation('nearest')
kepler.set_xlim(-0.5, x-0.5)
kepler.set_ylim(y-0.5, -0.5)

left.axes.get_xaxis().set_ticklabels([])
left.axes.get_yaxis().set_ticklabels([])
left.axes.get_xaxis().set_ticks([])
left.axes.get_yaxis().set_ticks([])

crval = w.wcs.crval
north = crval + np.array([0, 6/3600.])
east = crval + np.array([ 6/3600., 0])

ncoords = np.vstack([crval, north])
ecoords = np.vstack([crval, east])
npixels = w.wcs_world2pix(ncoords , 0)
epixels = w.wcs_world2pix(ecoords , 0)
npixels[1, 1] = npixels[0, 1] - (npixels[1, 1] - npixels[0, 1]) # flip ud
epixels[1, 1] = epixels[0, 1] - (epixels[1, 1] - epixels[0, 1])
if eo == 0:
   npixels[1, 0] = npixels[0, 0] - (npixels[1, 0] - npixels[0, 0]) # flip lr
   epixels[1, 0] = epixels[0, 0] - (epixels[1, 0] - epixels[0, 0])
kepler.plot(npixels[:,0], npixels[:,1], color='#00ff8c')
kepler.plot(epixels[:,0], epixels[:,1], '--', color='#00ff8c')

if ref == "y":
   print ' '
   if eo == 1:
      print '--> Reference pixel:'
      print '-----> RA =', refra
      print '-----> DEC =', refdec
      kepler.plot((x - refx) - 0.5, (y - refy) - 0.5, '*', color='#00ff8c', ms=10)
   elif eo == 0:
      print '--> Reference pixel:'
      print '-----> RA =', refra
      print '-----> DEC =', refdec
      kepler.plot(refx - 1.5, (y - refy) - 0.5, '*', color='#00ff8c', ms=10)
else:
   pass

right = ukirt.imshow(flux2, cmap='pink', norm=LogNorm())
ukirt.set_title('UKIRT Image')
right.set_interpolation('bilinear')
ukirt.set_xlim(300, 0)
ukirt.set_ylim(0, 300)

right.axes.get_xaxis().set_ticklabels([])
right.axes.get_yaxis().set_ticklabels([])
right.axes.get_xaxis().set_ticks([])
right.axes.get_yaxis().set_ticks([])

ukirt.plot([25, 25], [25, 55], '-', color='#00ff8c')
ukirt.plot([25, 55], [25, 25], '--', color='#00ff8c')

fig.set_size_inches(7.5, 4.5)
exec("plt.savefig('kic%dimg.png')" % kic)

print ' '
show = raw_input('--> Show plot now? (y/n) ')
while show != "y" and show != "n":
   show = raw_input('--> Please enter y or n: ')
print ' '
if show == "y":
   plt.show()
else:
   pass
