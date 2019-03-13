#!/usr/bin/python

# Install dependencies and restart Python3
#!pip install --upgrade pip
#!pip install numpy pandas rasterio matplotlib

import rasterio as rt
from rasterio.plot import show
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt
#Don't show scientific notation in Pandas:
pd.options.display.float_format = '{:.0f}'.format  

# Set Variables: 
print('***** Setting Variables:')
pop_density_threshold = 1000  ## population per square km...
print('Population Density Threshold:',pop_density_threshold,'people/km')
cold_threshold = 4.5 #Celcius 
warm_threshold = 30  #Celcius
print(cold_threshold*(9/5)+32,'to',warm_threshold*(9/5)+32)
chart_title_suffix = ' Masked for Comfortable Micromobility Use'

# Read in GeoTiff Files:
print('***** Read GeoTiff Files:')
#sedac.ciesin.columbia.edu/data/set/.../data-download
pop_density_rt = rt.open(r'pop/gpw_v4_population_density_rev11_2015_2pt5_min.tif')   
f= 'gpw_v4_population_count_adjusted_to_2015_unwpp_country_totals_rev11_2015_2pt5_min.tif'
pop_count_rt = rt.open(r'pop/'+f)

#http://worldclim.org/bioclim
climate_avg_rt = rt.open(r'climate/wc2.0_bio_2.5m_01.tif') #BIO1 =Annual Mean Temperature
climate_warm_rt = rt.open(r'climate/wc2.0_bio_2.5m_10.tif') #BIO10 =Mean of Warmest 3-mths
climate_cold_rt = rt.open(r'climate/wc2.0_bio_2.5m_11.tif') #BIO11 =Mean of Coldest 3-mths
print('DONE')

# Read the Rasters into np masked arrays: 
print('***** Read rasters into numpy masked arrays:')
pop_density = pop_density_rt.read(out_dtype=np.float64, masked=True)
pop_count = pop_count_rt.read(out_dtype=np.float_, masked=True)
climate_avg = climate_avg_rt.read(out_dtype=np.float64, masked=True)
climate_warm = climate_warm_rt.read(out_dtype=np.float64, masked=True)
climate_cold = climate_cold_rt.read(out_dtype=np.float64, masked=True)
print('DONE')

# Close the Raster data: 
print('***** Close Rasters')
pop_density_rt.close(); del pop_density_rt
pop_count_rt.close(); del pop_count_rt
climate_avg_rt.close(); del climate_avg_rt
climate_warm_rt.close(); del climate_warm_rt
climate_cold_rt.close(); del climate_cold_rt

# Gather stats on initial arrays: 
print('***** Gather stats on initial arrays:')
def get_stats(nparray, nosum='0'):
    # Calculate statistics for masked raster array and return as a dictionary:
    stats = {
        'min': nparray.min(),
        'mean': nparray.mean(),
        'max': nparray.max(),
        'sum': nparray.sum(),
        'count': nparray.count(),
        'count_masked': np.ma.count_masked(nparray),
        'size_ma': ma.size(nparray)}
    if nosum == 'nosum': stats['sum'] = None
    return stats

## Create a dictionary of dictionaries of stats on raster masked arrays:
overall_stats = {}
overall_stats['pop_density'] = get_stats(pop_density,'nosum')
overall_stats['pop_count'] = get_stats(pop_count)
overall_stats['cli_avg'] = get_stats(climate_avg,'nosum')
overall_stats['cli_warm'] = get_stats(climate_warm,'nosum')
overall_stats['cli_cold'] = get_stats(climate_cold,'nosum')
print('DONE')

# Compute World (base image), and Urban Density and Population arrays: 
print('***** Compute world, and population arrays:')
world = np.ma.masked_array(ma.ones(pop_density.shape), pop_density.mask)
pop_urban_density = ma.masked_where(pop_density < pop_density_threshold, pop_density)
overall_stats['pop_urb_dense']= get_stats(pop_urban_density,'nosum')
pop_urban = np.ma.masked_array(pop_count, pop_urban_density.mask)
overall_stats['pop_urban']= get_stats(pop_urban)
del pop_density # Free up some memory
print('DONE')

# Compute warm months and cold months arrays: 
print('***** Compute warm months and cold months arrays:')
warm_months = ma.masked_outside(climate_warm,cold_threshold,warm_threshold)
overall_stats['cli_warm_mths']= get_stats(warm_months,'nosum')

cold_months = ma.masked_outside(climate_cold,cold_threshold,warm_threshold)
overall_stats['cli_cold_mths']= get_stats(cold_months,'nosum')
print('DONE')

# Compute warm months and cold month population arrays: 
print('***** Compute warm months and cold month population arrays:')
pop_cold_months = np.ma.masked_array(pop_urban, cold_months.mask)
overall_stats['z_pop_cold']= get_stats(pop_cold_months)

pop_warm_months = np.ma.masked_array(pop_urban, warm_months.mask)
overall_stats['z_pop_warm']= get_stats(pop_warm_months)

combined_mask = cold_months.mask | warm_months.mask
pop_urban_full_yr = np.ma.masked_array(pop_urban, combined_mask)
overall_stats['z_pop_full_yr']= get_stats(pop_urban_full_yr)
print('DONE')

# Print out dataframe of results so far: 
print('***** Print out dataframe of results so far:')
print(pd.DataFrame.from_dict(overall_stats).T)

# Compute percents based on warm/cold three month data: 
print('***** Print percents based on warm/cold three month data:')
world_pop = overall_stats['pop_count']['sum']
urban_pop = overall_stats['pop_urban']['sum']

print('Pct Population in Urban:',round((urban_pop / world_pop)*100,0))
u= round((overall_stats['z_pop_warm']['sum'] / urban_pop)*100,0)
w= round((overall_stats['z_pop_warm']['sum'] / world_pop)*100,0)
print('Pct Warm Months:',u,w)
u= round((overall_stats['z_pop_cold']['sum'] / urban_pop)*100,0)
w= round((overall_stats['z_pop_cold']['sum'] / world_pop)*100,0)
print('Pct Cold Months:',u,w)
u= round((overall_stats['z_pop_full_yr']['sum'] / urban_pop)*100,0)
w= round((overall_stats['z_pop_full_yr']['sum'] / world_pop)*100,0)
print('Pct Full Year:',u,w)

# Compute average world-wide temperature weighted by population: 
print('***** Print average world-wide temperature weighted by population:')
   ### Need to fix the runtime overflow warning!!!
x=(climate_avg*pop_count).sum()/world_pop
print('avg temp:', round(x*(9/5)+32,1), round(x,1))
x=(climate_avg*pop_urban).sum()/urban_pop
print('avg temp (urban):', round(x*(9/5)+32,1), round(x,1))

x=(climate_warm*pop_count).sum()/world_pop
print('warm_avg temp:', round(x*(9/5)+32,1), round(x,1))
x=(climate_warm*pop_urban).sum()/urban_pop
print('warm_avg temp (urban):', round(x*(9/5)+32,1), round(x,1))

x=(climate_cold*pop_count).sum()/world_pop
print('cold_avg temp:', round(x*(9/5)+32,1), round(x,1))
x=(climate_cold*pop_urban).sum()/urban_pop
print('cold_avg temp (urban):', round(x*(9/5)+32,1), round(x,1))

del pop_count  # Free up some memory

# Create map of urban areas: 
print('***** Create map of urban areas:')

fig, ax = plt.subplots(1, figsize=(40, 20))
ax.axis('off')
## Set some max/min so that we supress the poles:
ax.set_ylim(bottom=3500, top=500)
ax.set_xlim(left=500, right=8000)
show(world, cmap='Set1_r', ax=ax)   
show(pop_urban, cmap='Set1', title='World Urban Areas', ax=ax)
ax.title.set_fontsize(40)
plt.savefig('images/urban_areas.png')
print('CREATED: images/urban_areas.png')

# Create map of coldest and warmest quarter averages masked: 
print('***** Create map of coldest and warmest quarter averages masked:')

fig, ax = plt.subplots(1, figsize=(12, 12))
ax.axis('off'); ax.set_ylim(bottom=3500, top=500)
show(world, cmap='Set1_r', ax=ax)
show(cold_months, cmap='coolwarm',
     title='Coldest Quarter Average'+chart_title_suffix, ax=ax)
plt.savefig('images/avg-cold-qt-mask.png')
print('CREATED: images/avg-cold-qt-mask.png')

fig, ax = plt.subplots(1, figsize=(12, 12))
ax.axis('off'); ax.set_ylim(bottom=3500, top=500)
show(world, cmap='Set1_r', ax=ax) 
show(warm_months, cmap='coolwarm', 
     title='Warmest Quarter Average'+chart_title_suffix, ax=ax)
plt.savefig('images/avg-warm-qt-mask.png')
print('CREATED: images/avg-warm-qt-mask.png')

# Create map of year round averages masked: 
print('***** Create map of year round averages masked:')
climate_avg_fullyear = np.ma.masked_array(climate_avg, combined_mask)

fig, ax = plt.subplots(1, figsize=(12, 12))
ax.axis('off'); ax.set_ylim(bottom=3500, top=500)
title='Overall Average Temperature'+chart_title_suffix

show(world, cmap='Set1_r', ax=ax) 
show(climate_avg_fullyear, cmap='coolwarm', title=title, ax=ax)
plt.savefig('images/avgtemp-yearround-mask.png')
print('CREATED: images/avgtemp-yearround-mask.png')

# Free up some memory: 
print('***** Free up some memory:')
del climate_avg; del climate_warm; del climate_cold; del combined_mask; 
del pop_urban_full_yr; del climate_avg_fullyear; del warm_months; del cold_months

# Create maps for each month masked: 
print('***** Create maps for each month masked:')

bymonth_out = {}  # Setup output dictionary
# Set up array of months:
mths = ['01','02','03','04','05','06','07','08','09','10','11','12']

for i in mths:
    # Open raster layer for given month: 
    avg_temp_rt = rt.open(r'climate/wc2.0_2.5m_tavg/wc2.0_2.5m_tavg_'+i+'.tif')
    # Read it into an numpy array:
    avg_temp = avg_temp_rt.read(out_dtype=np.float64, masked=True)
    avg_temp_rt.close()
    # Mask it based on the temp threshold: 
    temps_masked = ma.masked_outside(avg_temp,cold_threshold,warm_threshold)
    # Create an array of the masked urban population:
    useable_temp = ma.masked_array(pop_urban, temps_masked.mask)
    # Compute the stats and add to the dictionary of stats: 
    overall_stats[i]= get_stats(useable_temp)
    # Compute results (Percent Urban, Percent World, Avg Temperature-weighted)
    u= round((overall_stats[i]['sum'] / urban_pop)*100,1)
    w= round((overall_stats[i]['sum'] / world_pop)*100,1)
    temp= round((avg_temp*pop_urban).sum()/urban_pop*(9/5)+32,1)
    print(i,u,w,temp)
    # Store in the output dictionary:
    bymonth_out[i] = {'pop_urban_pct': u, 'pop_all_pct': w, 'avg_temp': temp}

    # Create map:
    fig, ax = plt.subplots(1, figsize=(12, 12))
    ax.axis('off'); ax.set_ylim(bottom=3500, top=500)
    title = i+'-Average Temp'+chart_title_suffix
    
    show(world, cmap='Set1_r', ax=ax) 
    show(temps_masked, cmap='coolwarm',  title=title, ax=ax)
    
    plt.savefig('mths/avgtemp-'+i+'-mask.png')
    print('CREATED: mths/avgtemp-'+i+'-mask.png')
    del avg_temp;    del temps_masked;    del useable_temp;    del avg_temp_rt

# Print month summary data: 
print('***** Print month summary data:')

mth_results = pd.DataFrame.from_dict(bymonth_out).T
mth_results.index.name = 'Month' # Name the "index" month
print(mth_results)

# Create chart for monthly data: 
print('***** Create chart for monthly data:')

mytitle = 'Percent Monthly Comfortable Micromobility Use & Temperature'
fig, ax = plt.subplots(1, figsize=(20, 12))
             
mth_results[['pop_all_pct','pop_urban_pct']].plot(kind='bar', color=['orange', 'red'], 
 												  title=mytitle, ax=ax)
mth_results[['avg_temp']].plot(linestyle='-', marker='o', c='b',linewidth=7.0, ax=ax)
  
mylabels = ['Average Temp','Percent World','Percent Urban']
plt.legend(fontsize=20, labels=mylabels)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(20)
ax.title.set_fontsize(30)
plt.savefig('images/month_chart.png')
print('CREATED: images/month_chart.png')
print('***** Process Complete')
print('Now run ffmpeg on the mths images and crop the other images for fit.')
