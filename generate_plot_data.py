import os
import json
import requests
import pandas as pd
import numpy as np
import reverse_geocoder as rg
from geopy.geocoders import Nominatim
import time

k = 3
sorts = [0,2,1]

folder='./k_data/'

"""
def old_gen_table_maplot():
    df = pd.read_csv(folder+'merged_labels.csv' )
    df = df[ (df['Latitude'].notna()) & (df['Latitude']<=90) & (df['Latitude']>=-90) & (df['Longitude']<=90) & (df['Longitude']>=-90) ]
    print(len(df))
    countryName=[]
    ds={}
    
    cc={}
    i=0
    f=open('cc_code.tsv','r')
    for line in f:
        l=line.replace('\n','').split('\t')
        if(i>0):
            cc[l[1].lower()]=l[0]
        i+=1
    f.close()
    
    geo={}
    geolocator = Nominatim(user_agent="geoapiExercises")
    for i in df.index:
        lat=df.loc[i, 'Latitude']
        lon=df.loc[i, 'Longitude']
        masterClass=df.loc[i, 'assignment']
        if(str(lat)!='nan' and str(lon)!='nan'):
            pair=str(lat)+","+str(lon)
            
            if(not pair in geo.keys()):
                location = geolocator.reverse(pair)
                adr=location.raw['address']
                name=adr['country']
                name=cc[adr['country_code']]
                geo[pair]=name
            else:
                name=geo[pair]
                
            countryName.append( name )
            if(not name in ds):
                ds[name]={}
                for j in range(0,5):
                    ds[name]['PC'+str(j)]=0
            ds[name]['PC'+str(masterClass)]+=1
                
    df['CountryName']=countryName
    df.to_csv(folder+'dat_plot2_countryName.csv', index=None)
    
    f=open('dat_plot2.csv','w')
    f.write('location,pca,count\n')
    for k in ds.keys():
        keys=list(ds[k].keys())
        vals=list(ds[k].values())
        ind=np.argmax(vals)
        p=keys[ind]
        v=vals[ind]
        f.write('"%s",%i,%i\n' %(k, int(p.replace('PC',''))+1, v))
    f.close()    
"""

def auxiliar_map_country_name():
    dat={}
    df = pd.read_csv(folder+'dat_plot2_countryName.csv' )
    
    for i in df.index:
        name = df.loc[i, 'CountryName']
        sample=df.loc[i, 'Sample']
        dat[sample]=name
    with open('map_country_names.json', 'w') as fp:
        json.dump(dat, fp)
    
def step1_gen_table_barplot(k):
    subfolder='data_k-'+str(k)+'/'
    df = pd.read_csv(folder+'pcs/merged_pruned_all.'+str(k)+'.Q' , sep=' ', header=None)
    df1 = pd.read_csv(folder+'merged_pruned_all.fam', sep=' ', header=None)
    dfs = df.set_index(df1[1])
    dfs.index.names = ['IND']
    dfs = dfs.sort_values(by=sorts)
    dfs.to_csv(folder+subfolder+'sorted_plot1.csv')

def step2_gen_table_maplot_allSource(k):
    subfolder='data_k-'+str(k)+'/'
    df = pd.read_csv(folder+subfolder+'merged_labels.csv' )
    
    with open('map_country_names.json') as f:
        dat=json.load(f)
    
    ds={}
    for j in range(0, int(k)):
        ds['PC'+str(j)]={}
                
    total_country={}
    for i in df.index:
        sample = df.loc[i, 'Sample']
        masterClass=df.loc[i, 'assignment']
        if(sample in dat.keys()):
            name=dat[sample]
            
            if(not name in total_country.keys() ):
                total_country[name]=0
            if(not name in ds['PC'+str(masterClass)].keys() ):
                ds['PC'+str(masterClass)][name]=0
                
            total_country[name]+=1
            ds['PC'+str(masterClass)][name]+=1
    
    f=open(folder+subfolder+'dat_plot2_allSource.csv','w')
    f.write('pca,location,count,total_country,percentage\n')
    for pca in ds.keys():
        for country in ds[pca].keys():
            perc = (ds[pca][country]/total_country[country])*100
            f.write('%s,"%s",%i,%i,%.2f\n' %(pca, country, ds[pca][country], total_country[country], perc) )
    f.close()    

def _get_mapping_class_superpopulation(k):
    subfolder='data_k-'+str(k)+'/'
    
    df = pd.read_csv(folder+subfolder+'merged_labels.csv' )
    df=df[ (~df['Source'].isna()) ]
    dat={}
    for i in df.index:
        clas='class-'+str(df.loc[i, 'assignment'])
        superpop=df.loc[i, 'Superpopulation']
        
        if(not clas in dat.keys()):
            dat[clas]={}
        if(not superpop in dat[clas].keys()):
            dat[clas][superpop]=0
            
        dat[clas][superpop]+=1
        
    mapping={}
    for k in dat.keys():
        counts = list(dat[k].values())
        superpop_major = list(dat[k].keys())
        mapping[k] = superpop_major[ np.argmax(counts) ]
    return mapping
            
def step3a_inference_superpopulation_plco(k):
    subfolder='data_k-'+str(k)+'/'
    
    mapp = _get_mapping_class_superpopulation(k)
    
    cols=['Sample']
    for j in range(0, int(k)):
        cols.append(str(j))
    cols.append('assignment')
    
    df = pd.read_csv(folder+subfolder+'merged_labels.csv' )
    df=df[ (df['Source'].isna()) ][ cols ]
    superpop = []
    for i in df.index:
        clas = 'class-'+str(df.loc[i, 'assignment'])
        superpop.append(mapp[clas])
    df['inferred_superpopulation'] = superpop
    df.to_csv(folder+subfolder+'plco_inferred_superpop.tsv', index=None, sep='\t')    


def _get_countries_by_region():
    response = requests.get('https://www.dhs.gov/geographic-regions')
    text=response.text
    lines = text.split('\n')
    dat={}
    key=''
    flag=False
    for l in lines:
        if(l.find('class="usa-accordion__button"')!=-1):
            key=l.split('>')[1].split('<')[0]
            dat[key]=[]
            flag=True
            
        if(flag and l.find('<li>')!=-1):
            dat[key].append( l.split('<li>')[1].split('<')[0] )
        
        if(flag and l.find('</ul></div>')!=-1):
            flag=False
            
    with open('map_countries_region.json','w') as fp:
        json.dump(dat, fp)
        
def step3b_prepare_table_plco_map(k):
    subfolder='data_k-'+str(k)+'/'
    
    with open('map_countries_region.json') as fp:
        geo=json.load(fp)
    
    df = pd.read_csv(folder+subfolder+'plco_inferred_superpop.tsv', sep ='\t')
    ds={}
    for j in range(0, int(k)):
        ds['PC'+str(j)]={}
                
    total_country={}
    for i in df.index:
        pop = df.loc[i, 'inferred_superpopulation']
        masterClass=df.loc[i, 'assignment']
        ok=None
        for k in geo.keys():
            if( pop.find(k)!=-1 ):
                ok=k
                break
                
        if( ok!=None ):
            for name in geo[ok]:
                if(not name in total_country.keys() ):
                    total_country[name]=0
                if(not name in ds['PC'+str(masterClass)].keys() ):
                    ds['PC'+str(masterClass)][name]=0
                    
                total_country[name]+=1
                ds['PC'+str(masterClass)][name]+=1
    
    f=open(folder+subfolder+'dat_plot3_plco.csv','w')
    f.write('pca,location,count,total_country,percentage\n')
    for pca in ds.keys():
        for country in ds[pca].keys():
            perc = (ds[pca][country]/total_country[country])*100
            f.write('%s,"%s",%i,%i,%.2f\n' %(pca, country, ds[pca][country], total_country[country], perc) )
    f.close()   
    
def prepare_other_components():
    pcs=[]
    folder='k_data/'
    
    df = pd.read_csv(folder+'reference_panel_metadata.tsv', sep ='\t')
    df1 = pd.read_csv(folder+'merged_pruned_all.fam', sep=' ', names=[0,'Sample',2,3,4,5])
    dfs = pd.merge(df1['Sample'], df, on='Sample', how='left')
    for p in os.listdir(folder+'pcs'):
        k = int( p.split('.')[1] )
        pcs.append(str(k))
        
        sorts = [ i for i in range(k)]
        
        kfolder=folder+'/data_k-'+str(k)
        if(not os.path.isdir(kfolder)):
            os.system('mkdir '+kfolder)
        
        df = pd.read_csv(folder+'pcs/merged_pruned_all.%d.Q' % k , sep=' ', header=None)
        df['assignment'] = df.idxmax(axis=1)
        df['Sample'] = dfs['Sample']
        df =  dfs.merge(df, on='Sample', how='left')
        df.to_csv(kfolder+'/merged_labels.csv', index=None)
        
        step1_gen_table_barplot(k)
        step2_gen_table_maplot_allSource(k)
        step3a_inference_superpopulation_plco(k)
        step3b_prepare_table_plco_map(k)
        
    f=open('pcs_available.tsv','w')
    f.write(','.join(pcs)+'\n')
    f.close()
    
#gen_table_barplot()
#gen_table_maplot()
#inference_superpopulation_plco()
#gen_table_maplot_allSource()
#auxiliar_map_country_name()
#_get_countries_by_region()
prepare_other_components()
      
# https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json
# https://github.com/thampiman/reverse-geocoder
# https://plotly.com/javascript/choropleth-maps/
# https://plotly.com/javascript/figure-labels/

# autoencoder instead of neura admixture - https://blog.keras.io/building-autoencoders-in-keras.html

# https://colab.research.google.com/drive/1EptY1oGYVlQUrMR6itfQX7T1YAEXZFt1#scrollTo=0RH7wAP2K8tb
