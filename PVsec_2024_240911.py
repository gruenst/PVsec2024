import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import itertools
import warnings
import seaborn as sns
warnings.filterwarnings("ignore")
Torgau = pvlib.location.Location(latitude=51.57167043667758, longitude=12.999655206598819, tz='Europe/Berlin') 
Muenchen = pvlib.location.Location(latitude=48.08835590454616, longitude=11.650823666536375, tz='Europe/Berlin')
Mokropsy = pvlib.location.Location(latitude=49.941049, longitude=14.321330, tz='Europe/Berlin')

###!!!!!---    site selection:   Torga, Muenchen, Mokropsy
site = Torgau
###!!!!!----

if (site == Torgau):
    print("Site Torgau, loading data file...")
    df = pd.read_csv("C:\\Temp\\PVsec_2024\\Torgau.csv",delimiter=';',index_col=0,parse_dates=True,date_parser=lambda x: dt.datetime.strptime(x, '%d.%m.%Y %H:%M'))
    df.rename(columns={"irr_S[W/m2]": "irr_S", "irr_N[W/m2]": "irr_N", "irr_E[W/m2]": "irr_E", "irr_W[W/m2]": "irr_W", "irr_HOR[W/m2]": "irr_HOR"},inplace=True)
    excludeDays = ['2022-11-19','2022-11-21','2022-12-02','2022-12-03','2022-12-04','2022-12-10','2022-12-11','2022-12-12','2023-01-19','2023-01-20','2023-01-21','2023-03-08','2023-03-09','2023-11-26','2023-11-27','2023-11-28','2023-11-29','2023-11-30','2023-12-01','2023-12-02','2024-01-12','2024-01-13','2024-01-16','2024-01-18','2024-01-19','2024-01-20','2024-01-21','2024-01-22']
    excludeHours = []
elif (site == Muenchen):    
    print("Site Muenchen, loading data file...")
    df = pd.read_csv("C:\\Temp\\PVsec_2024\\Muenchen.csv",delimiter=';',index_col=0,parse_dates=True,date_parser=lambda x: dt.datetime.strptime(x, '%d.%m.%Y %H:%M'))
    df.rename(columns={"South": "irr_S", "North": "irr_N", "East": "irr_E", "West": "irr_W", "Horizontal": "irr_HOR"},inplace=True)
    excludeDays = ['2022-04-02','2022-04-03','2022-04-04','2022-04-11','2022-04-25','2022-12-10','2022-12-11','2022-12-12','2023-01-19','2023-01-20','2023-01-21','2023-03-18','2023-03-19','2023-03-20','2023-03-21','2023-03-22','2023-03-23','2023-03-24','2023-03-25','2023-12-02','2023-12-03','2023-12-04','2023-12-05','2023-12-06','2023-12-07','2023-12-08','2023-12-09','2023-12-10','2024-01-07','2024-01-08','2024-01-09','2024-01-10','2024-01-11','2024-01-12','2024-01-13','2024-01-14','2024-01-15','2024-01-16','2024-01-17','2024-01-19','2024-01-20']
    excludeHours = []
elif (site == Mokropsy):    
    print("Site Mokropsy, loading data file...")
    df = pd.read_csv("C:\\Temp\\PVsec_2024\\Mokropsy.csv",delimiter=';',index_col=0,parse_dates=True,date_parser=lambda x: dt.datetime.strptime(x, '%d.%m.%Y %H:%M'))
    df.rename(columns={"irr_hor[W/m2]": "irr_HOR", "irr_SW[W/m2]": "irr_SW", "irr_SE[W/m2]": "irr_SE","irr_S[W/m2]":"irr_SSE"},inplace=True)
    excludeDays = ['2019-12-12','2020-01-20','2020-02-28','2020-02-29','2020-12-03','2021-01-06','2021-01-07','2021-01-08','2021-01-09','2021-01-10','2021-01-12','2021-01-13','2021-01-14','2021-01-15','2021-01-16','2021-01-21','2021-01-26','2021-01-27','2021-01-29','2021-02-06','2021-02-07','2021-02-08','2021-02-09','2021-03-08','2021-03-10','2021-03-17','2021-03-19','2021-03-20','2021-04-06','2021-04-07','2021-04-16','2021-11-28','2021-11-29','2021-11-30','2021-12-01','2021-12-09','2021-12-10','2021-12-25','2021-12-26','2022-01-09','2022-01-08','2022-01-21','2022-03-04','2022-11-19','2022-12-11','2022-12-12','2022-12-16','2022-12-17','2023-01-21','2023-01-22','2023-01-23','2023-02-26','2023-03-05','2023-03-11','2023-11-18','2023-11-19','2023-11-28','2023-11-29','2023-11-30','2023-12-01','2023-12-02','2023-12-03','2023-12-04','2023-12-05','2023-12-06','2023-12-22','2024-01-19']
    excludeHours = []   

df['hours'] = df.index.hour
if (excludeDays != []):
    df = df.drop(pd.concat([df.loc[date] for date in excludeDays]).index)
if (excludeHours != []):
    test = df.drop(df[df.hours.isin(excludeHours)].index)
    df.drop(columns='hours')


#%% correct timestamps to fit clearsky data
print("correcting time shifts....")
leapDays = np.unique([day.date() for day in df.index if (((day.month==3) or (day.month==10)) and (day.dayofweek==6) and (31-day.day<7) or (day==df.index[0]) )])  #gives list of dates of time change 
timeParts = [df[leapDays[i].ctime():leapDays[i+1].ctime()] for i in range(len(leapDays)-1)] # split data set by leapDays
timeParts.append(df[leapDays[-1]:])  # ... and put the parts into one list, including the remaining days
for timePart in timeParts:  # loop for each time interval
   csStart = site.get_clearsky(timePart.index)    # starting conditions
   correlOld = csStart['ghi'].corr(timePart['irr_HOR'])
   timeShifter = dt.timedelta(hours=2)
   plusMinus = True
   while(timeShifter > dt.timedelta(minutes=5)):  # loop to optimize time stamp
     timePart.index = timePart.index + plusMinus * timeShifter - (not plusMinus)*timeShifter
     csNew = site.get_clearsky(timePart.index)
     correlNew = csNew['ghi'].corr(timePart['irr_HOR'])
     if correlNew <= correlOld:
       plusMinus = not plusMinus  # invert plus/minus
       timePart.index = timePart.index + plusMinus * timeShifter - (not plusMinus)*timeShifter  #undo change
       if (plusMinus):
         if timeShifter > dt.timedelta(minutes=15): timeShifter /= 2
         else: timeShifter -= dt.timedelta(minutes=5)
     else:
       correlOld, csStart = correlNew, csNew
df = pd.concat(timeParts)
print("sorting index, filtering duplicates...")
df=df.sort_index().drop_duplicates()

#%% Night Offset Correction - cycle through every day and subtract pyranometer offset
print("applying night time offset correction...")
if (site != Mokropsy):
  for day in df.index.round(freq='d').sort_values().unique():
    try:
      if np.isnan(np.average(df[(df.index.date == day) &  ((df.index.hour < 4)  |  (df.index.hour > 23) ) ]['irr_HOR'])):
        df = df.drop(pd.concat([df.loc[day.strftime('%Y-%m-%d')]]).index)
      else:
        df.loc[df.index.date == day, 'irr_HOR'] -=  np.average(df[(df.index.date == day) &  ((df.index.hour < 4)  |  (df.index.hour > 23) ) ]['irr_HOR'])
    except:
      continue
#%%  SPLIT  GHI into   DHI (diffuse) and DNI (direct normal)
arrayRMSE, arrayMBE, rRMSE_N,rRMSE_E, rRMSE_S, rRMSE_W, rRMSE_SE, rRMSE_SW, rRMSE_SSE, rMBE_N, rMBE_E, rMBE_S, rMBE_W, rMBE_SW, rMBE_SE, rMBE_SSE = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
max_zenith = 87
min_cos_zenith=0.065
for i,j in itertools.product(range(1,9,1),range(1,8,1)):
    print("loop number {},{}".format(i,j))
    dni_select = i
    #1: DIRINT
    if dni_select == 1:
      dni = pvlib.irradiance.dirint(ghi=df['irr_HOR'], solar_zenith=site.get_solarposition(df.index)['zenith'], times=df.index, pressure=pvlib.atmosphere.alt2pres(site.altitude), use_delta_kt_prime=True, temp_dew=None, min_cos_zenith=min_cos_zenith, max_zenith=max_zenith)
      dhi = pvlib.irradiance.complete_irradiance(solar_zenith=site.get_solarposition(df.index)['apparent_zenith'], ghi=df['irr_HOR'], dni=dni,dhi=None,dni_clear=site.get_clearsky(df.index)['dni'])['dhi']
    #2: DIRINDEX
    if dni_select == 2:
      dni = pvlib.irradiance.dirindex(ghi=df['irr_HOR'], ghi_clearsky=site.get_clearsky(df.index)['ghi'], dni_clearsky=site.get_clearsky(df.index)['dni'], zenith=site.get_solarposition(df.index)['zenith'], times=df.index, pressure=pvlib.atmosphere.alt2pres(site.altitude), use_delta_kt_prime=True, temp_dew=None, min_cos_zenith=min_cos_zenith, max_zenith=max_zenith)
      dhi = pvlib.irradiance.complete_irradiance(solar_zenith=site.get_solarposition(df.index)['apparent_zenith'], ghi=df['irr_HOR'], dni=dni,dhi=None,dni_clear=site.get_clearsky(df.index)['dni'])['dhi']
    #3: DISC
    elif dni_select == 3:
      dni = pvlib.irradiance.disc(df['irr_HOR'], site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, pressure=None, min_cos_zenith=min_cos_zenith, max_zenith=max_zenith, max_airmass=12)['dni']
      dhi = pvlib.irradiance.complete_irradiance(solar_zenith=site.get_solarposition(df.index)['apparent_zenith'], ghi=df['irr_HOR'], dni=dni,dhi=None,dni_clear=site.get_clearsky(df.index)['dni'])['dhi']
    #4: Erbs
    elif dni_select == 4:
      dni = pvlib.irradiance.erbs(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dni']
      dhi = pvlib.irradiance.erbs(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dhi']
    #5: Erbs-Driesse
    elif dni_select == 5:
      dni = pvlib.irradiance.erbs_driesse(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, dni_extra=None, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dni']
      dhi = pvlib.irradiance.erbs_driesse(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, dni_extra=None, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dhi']
    #6: Orgill-Hollands
    elif dni_select == 6:
      dni = pvlib.irradiance.orgill_hollands(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, dni_extra=None, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dni']
      dhi = pvlib.irradiance.orgill_hollands(ghi=df['irr_HOR'], zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, dni_extra=None, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dhi']
    #7: Boland
    elif dni_select == 7:
      dni = pvlib.irradiance.boland(ghi=df['irr_HOR'], solar_zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dni']
      dhi = pvlib.irradiance.boland(ghi=df['irr_HOR'], solar_zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith, min_cos_zenith=min_cos_zenith)['dhi']
    #8: Louche
    elif dni_select == 8:
      dni = pvlib.irradiance.louche(ghi=df['irr_HOR'], solar_zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith)['dni']
      dhi = pvlib.irradiance.louche(ghi=df['irr_HOR'], solar_zenith=site.get_solarposition(df.index)['zenith'], datetime_or_doy=df.index, max_zenith=max_zenith)['dhi']
    
    #%   POA irradiance
    if site in [Torgau, Muenchen]:
      azAngles = [0,90,180,270]  #  azimuth from North=0
    elif (site == Mokropsy):
      azAngles = [132,221,158]#[139,213,167]
    for az in azAngles:     
        print("Azimuth: {}".format(az))
        if site==Torgau:  az += 6  # cube Torgau is tilted by 5° clockwise
        tilt, albedo = 90, 0.20   #  tilt from horizontal,  albedo:best 0.24 for haydavies
        i_model = j
        if i_model == 1:
          model = 'isotropic'
        elif i_model == 2:
          model = 'klucher'
        elif i_model == 3:
          model = 'haydavies'  
        elif i_model == 4:
          model = 'reindl'
        elif i_model == 5:
          model = 'king'
        elif i_model == 6:
          model = 'perez'
        elif i_model == 7:
          model = 'perez-driesse'
        if i_model in [3,4,6,7]:
          poa = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt, surface_azimuth=az, solar_zenith=site.get_solarposition(df.index)['apparent_zenith'], solar_azimuth=site.get_solarposition(df.index)['azimuth'], dni=dni, ghi=df['irr_HOR'], dhi=dhi, dni_extra=pvlib.irradiance.get_extra_radiation(df.index), albedo=albedo, airmass=site.get_airmass(df.index)['airmass_relative'],model=model)['poa_global']
        else:
          poa = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt, surface_azimuth=az, solar_zenith=site.get_solarposition(df.index)['apparent_zenith'], solar_azimuth=site.get_solarposition(df.index)['azimuth'], dni=dni, ghi=df['irr_HOR'], dhi=dhi, dni_extra=None, albedo=albedo, airmass=None,model=model)['poa_global']
        
        #%    plot / evaluation
        #ax = df['irr_N'].plot()
        #poa.plot(ax=ax)
        #poa_p = poa.resample('H').mean()
        if site==Torgau:  az -= 6  # ...for making classifications easier...
        if az == 0:  
          irr = df['irr_N']
          rRMSE_N.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_N.append((irr-poa).mean()/irr.mean())
          poa_N = poa
        elif az == 90:  
          irr = df['irr_E']
          rRMSE_E.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_E.append((irr-poa).mean()/irr.mean())
          poa_E = poa
        elif az == 180:  
          irr = df['irr_S']
          rRMSE_S.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_S.append((irr-poa).mean()/irr.mean())
          poa_S = poa
        elif az == 270:  
          irr = df['irr_W']
          rRMSE_W.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_W.append((irr-poa).mean()/irr.mean())
          poa_W = poa
        elif az == 132:     #MOKROPSY
          irr = df['irr_SE']
          rRMSE_SE.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_SE.append((irr-poa).mean()/irr.mean())
          poa_SE = poa
        elif az == 221:     #MOKROPSY
          irr = df['irr_SW']
          rRMSE_SW.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_SW.append((irr-poa).mean()/irr.mean())
          poa_SW = poa
        elif az == 158:     #MOKROPSY
          irr = df['irr_SSE']
          rRMSE_SSE.append(((((irr-poa) ** 2).mean()) **.5) / irr.mean())
          rMBE_SSE.append((irr-poa).mean()/irr.mean())
          poa_SSE = poa

        # data filtering for azimuth and elevation angles
        data = pd.DataFrame({'irr':irr,'poa':poa,'az':site.get_solarposition(df.index)['azimuth'], 'el': site.get_solarposition(df.index)['elevation']},index=df.index)
        if (site==Muenchen):
          data = data.loc[(((data.el > 20)  | (data.az >130)) & (data.el > 20 * (data.az-180)/100))]
        if (site==Torgau):
          data = data.loc[(((data.el > 11)  | (data.az <200)) & (data.el > -45 * (data.az-180)/100))]
        if (site==Mokropsy):
          data = data.loc[(((data.el > 8)  & (data.az >110)) & (data.el > 20 * (data.az-180)/100))]
          data = data.loc[(data.irr > 500)]

        xValues = np.linspace(60,300,100)  # azimuth from 60 to 300
        yValues = np.linspace(0,80,100)  # elevation between 10 and 80
        aMBE = np.empty((100,100,))
        aMBE[:] = np.nan   # array of NANs
        aRMSE = np.empty((100,100,))
        aRMSE[:] = np.nan   # array of NANs
        nPlot = np.empty((100,100,))
        nPlot[:] = np.nan   # array of NANs
        for k in range(100):
            if (k % 10 == 0):  print("{}% complete".format(k))
            for l in range(100):
                azMin = xValues[k] - (xValues[1]-xValues[0])/2
                azMax = xValues[k] + (xValues[1]-xValues[0])/2
                elMin = yValues[l] - (yValues[1]-yValues[0])/2
                elMax = yValues[l] + (yValues[1]-yValues[0])/2
                aMBE[l,k] = (data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").irr-data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").poa).mean()/data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").irr.mean()
                aRMSE[l,k] = ((((data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").irr-data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").poa) ** 2).mean()) ** .5) / (data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").irr .mean())
                nPlot[l,k] = data.query("az>= @azMin and az< @azMax and el >= @elMin and el< @elMax").irr.count()
        arrayRMSE.append(aRMSE)
        arrayMBE.append(aMBE)
      
    

#%%   Plot  rRMSE or rMBE   

index = 0  # for plotting purpose, select direction:  North, East, South, West, SE, SW, SSE
if (index==0): direction = "North"
elif (index==1): direction = "East"
elif (index==2): direction = "South"
elif (index==3): direction = "West"
elif (index==4): 
  direction = "South-East" #Mokropsy Only
  index -= 4
elif (index==5): 
  direction = "South-West" #Mokropsy Only
  index -= 4
elif (index==6): 
  direction = "South-South-East" #Mokropsy Only
  index -= 4


switch = 1  # select beetween rMBE or rRMSE
f, ax = plt.subplots()
if (switch==0): 
  mesh = ax.pcolormesh(xValues,yValues,arrayMBE[index],cmap='magma',vmax=0.5,vmin=-0.5)
  switchText = "rMBD"
elif (switch==1): 
  mesh = ax.pcolormesh(xValues,yValues,arrayRMSE[index],cmap='magma',vmax=0.5,vmin=0)
  switchText = "rRMSD"
elif (switch==2): 
  mesh = ax.pcolormesh(xValues,yValues,nPlot,cmap='magma',vmax=40,vmin=0)
  switchText = "n"
f.colorbar(mesh,ax=ax)
ax.figure.draw(ax.figure.canvas.get_renderer())
#ax.invert_xaxis()
ax.set_ylabel('elevation')
ax.set_xlabel('azimuth')
plt.ylim(top=80,bottom=0)
if (site==Torgau):
  ax.set_title("Torgau, {}, {}".format(direction,switchText))
elif (site==Muenchen):
  ax.set_title("Munich, {}, {}".format(direction,switchText))
elif (site==Mokropsy):
  ax.set_title("Mokropsy, {}, {}".format(direction,switchText))

