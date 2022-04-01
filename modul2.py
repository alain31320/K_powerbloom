import csv
import os
import requests
import urllib.parse
import folium
from folium import features, FeatureGroup, Marker, LayerControl
from folium.features import DivIcon
import requests
import urllib.parse
import numpy as np
from time import sleep

def Tranchlist(kk,n):
    i,j = int(len(kk)/n),len(kk)%n
    xx = []
    for i0 in range(i):
        u = kk[i0*n:(i0+1)*n]
        xx.append(u)
    v = kk[n*i:len(kk)]
    if len(v)>0:
        xx.append(v)
    print(xx)
    return xx
    
def calculdist2(coor1,coor2):
    from math import sin, cos, sqrt, atan2, radians

    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(coor1[0])
    lon1 = radians(coor1[1])
    lat2 = radians(coor2[0])
    lon2 = radians(coor2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    formatted_string = "{:.3f}".format(distance)
    distance = float(formatted_string)
    return distance

def getaddr(lat,lon):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="html")
    add = str(lat)+', '+str(lon)
    location = geolocator.reverse(add)
    rlo = (location[-1],location[-3])
    return rlo

def getlatlon(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    response = requests.get(url).json()
    lat = response[0]["lat"]
    lon = response[0]["lon"]
    ll = (float(lat),float(lon))
    return ll
def strz(aa):
    if len(aa)>0:
        n=float(aa)
    else:
        n=0
    return n
def makeadress(addr,city,country):
    toutad = addr + ', ' + city + ', ' + country
    return toutad

def isfranceouteur2(lat,lon):
    import numpy as np
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="html")
    gpss = str(lat)+', '+str(lon)
    location = geolocator.reverse(gpss)
    location=location.address.split(',')
    if set('france').issubset(set(location[-1].lower())):
        rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
        rep1=rep+'gpsdep.npy'
        LcoordD = np.load(rep1);
        ll2=[calculdist2((lat,lon),(float(ii[0]),float(ii[1]))) for ii in LcoordD]
        if (list(LcoordD[ll2.index(min(ll2))])[2] in ['2A','2B']):
            xlo = 'corse'
        elif (list(LcoordD[ll2.index(min(ll2))])[2] in ['971','972','973','974','976']):
            xlo = 'outrem'
        else:
            xlo = 'france'
    elif set('unitedkingdom').issubset(set(location[-1].lower())):
        xlo = 'unitedkingd'
    else:
        xlo = 'general'
    print(xlo)
    return xlo


def Deptrech(lat,lon):
    
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'DicFront.npy'
    DicFront = np.load(rep1,allow_pickle=True);
    DicFront=DicFront.tolist()
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'gpsdep.npy'
    LcoordD = np.load(rep1);
    ll2=[calculdist2((lat,lon),(float(ii[0]),float(ii[1]))) for ii in LcoordD]
    mini=LcoordD[ll2.index(min(ll2))][2]
    aa=str(mini)
    print(aa)
    XX=list(set(DicFront[aa]))
    XY = [ii[:2] for ii in XX];XY.append(aa)
    return XY

def extra_corse(lat,lon,dism,Pmin,Pmax):
    import numpy
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'gpsCor.npy'
    LcoordSourceCor = numpy.load(rep1);

    dism,Pmin,Pmax=int(dism),int(Pmin),int(Pmax)
    La=[i for i in range(len(LcoordSourceCor)) if calculdist2((lat,lon),(float(LcoordSourceCor[i][0]),
        float(LcoordSourceCor[i][1]))) < dism]

    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'sourceCor.npy'
    LSourceCor = numpy.load(rep1,allow_pickle=True);
    L11=[LSourceCor[i] for i in La]
    Pui = [max([strz(ii['Puissance installée (kW)']),strz(ii['puisMaxRacCharge']),strz(ii['puisMaxCharge'])
        ,strz(ii['puisMaxRac'])]) for ii in L11]

    Li=[Pui.index(ii) for ii in Pui if ((ii>=Pmin) and (ii<=Pmax))]
    Lrc = [tuple(L11[i]['geo_point_2d'].split(',')) for i in Li]
    Lrc = [(float(i[0]),float(i[1])) for i in Lrc] 
    Lr2 = [(L11[i]['Code installation'],L11[i]['Filière'],Pui[i]) for i in Li]
    La2=[calculdist2((lat,lon),(float(ii[0]),float(ii[1]))) for ii in Lrc]
    Lr3 = [(L11[i]['Commune'],L11[i]['Date mise en service'],
            L11[i]['DateDebutVersion'],L11[i]['Tension de raccordement'],L11[i]['modeRaccordement']) for i in Li]
    Lr3 = [(Lr3[i][0],Lr3[i][1],Lr3[i][2],Lr3[i][3],Lr3[i][4],La2[i]) for i in range(len(Lr3))]

    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'CorresCor.npy'
    LCorCor = numpy.load(rep1,allow_pickle=True);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'ListEnCor.npy'
    LEnCor = numpy.load(rep1,allow_pickle=True);
    Lri3 = [L11[i]['Filière'] for i in Li]
    tt=[list(LEnCor).index(ii) for ii in Lri3]
    Licon=[LCorCor[i].lower()+'.png' for i in tt]
    print(Lrc);print(Lr2);print(Licon)
    return Lrc,Lr2,Lr3,Licon

def extra_outre(lat,lon,dism,Pmin,Pmax):
    import numpy
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'gpsOum.npy'
    dism,Pmin,Pmax=int(dism),int(Pmin),int(Pmax)
    LcoordSourceOum = numpy.load(rep1);
    La=[i for i in range(len(LcoordSourceOum)) if calculdist2((lat,lon),(float(LcoordSourceOum[i][0]),
    float(LcoordSourceOum[i][1]))) < dism]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'sourceOum.npy'
    LSourceOum = numpy.load(rep1,allow_pickle=True);
    L11=[LSourceOum[i] for i in La]
    Pui = [max([strz(ii['Puissance installée (kW)']),strz(ii['puisMaxRacCharge']),strz(ii['puisMaxCharge'])
    ,strz(ii['puisMaxRac'])]) for ii in L11]
    Li=[Pui.index(ii) for ii in Pui if ((ii>=Pmin) and (ii<=Pmax))]
    Lrc = [tuple(L11[i]['geo_point_2d'].split(',')) for i in Li]
    Lrc = [(float(i[0]),float(i[1])) for i in Lrc] 
    Lr2 = [(L11[i]['Code installation'],L11[i]['Filière'],Pui[i]) for i in Li]
    La2=[calculdist2((lat,lon),(float(ii[0]),float(ii[1]))) for ii in Lrc]
    Lr3 = [(L11[i]['Commune'],L11[i]['Date mise en service'],L11[i]['DateDebutVersion'],L11[i]['Tension de raccordement'],L11[i]['modeRaccordement']) for i in Li]
    Lr3 = [(Lr3[i][0],Lr3[i][1],Lr3[i][2],Lr3[i][3],Lr3[i][4],La2[i]) for i in range(len(Lr3))]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'CorresOu.npy'
    LCorOum = numpy.load(rep1,allow_pickle=True);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'ListEnOu.npy'
    LEnCor = numpy.load(rep1,allow_pickle=True);
    Lri3 = [L11[i]['Filière'] for i in Li]
    tt=[list(LEnCor).index(ii) for ii in Lri3]
    Licon=[LCorOum[i].lower()+'.png' for i in tt]
    return Lrc,Lr2,Lr3,Licon

def extra_france(lat,lon,dism,Pmin,Pmax):
    lld=Deptrech(lat,lon)
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    Sx=[]
    for gg in lld:
        rep1=rep+'latlon'+'_'+gg+'.npy'
        Llatlon = np.load(rep1);
        Llatlon=Llatlon.tolist()
        Llatlon=[tuple(ii) for ii in Llatlon]
        Sx.extend(Llatlon)
    print(len(Sx))
    La0=[calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) for i in range(len(Sx))]
    print((min(La0),max(La0)))
    dism = int(dism)
    La=[i for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    La2=[Sx[i] for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    Sy=[]
    for gg in lld:
        rep1=rep+'region_'+gg+'.npy'
        LSourc = np.load(rep1,allow_pickle=True);
        LSourc = LSourc.tolist()
        Sy.extend(LSourc)
    Pmin,Pmax = int(Pmin),int(Pmax)
    LL=[Sy[i] for i in La];La01=[La0[i] for i in La];print(La01);print('----------------------')
    Pui = [max([strz(ii['puisMaxInstallee']),strz(ii['puisMaxRacCharge']),strz(ii['puisMaxCharge'])
                ,strz(ii['puisMaxRac'])]) for ii in LL]
    Li=[Pui.index(ii) for ii in Pui if ((ii>=Pmin) and (ii<=Pmax))]
    Lrc = [La2[i] for i in Li];La02=[La01[i] for i in Li];print(La02)
    Lr2 = [(LL[i]['codeEICResourceObject'],LL[i]['filiere'],Pui[i]) for i in Li]
    La2=[calculdist2((lat,lon),(float(ii[0]),float(ii[1]))) for ii in Lrc]
    Lr3 = [(LL[i]['commune'],LL[i]['dateMiseEnService'],LL[i]['dateDebutVersion'],
            LL[i]['tensionRaccordement'],LL[i]['modeRaccordement']) for i in Li]
    Lr3 = [(Lr3[i][0],Lr3[i][1],Lr3[i][2],Lr3[i][3],Lr3[i][4],La02[i]) for i in range(len(Lr3))]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'CorresFr.npy'
    LCorFr = np.load(rep1,allow_pickle=True);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'ListEnFr.npy'
    LEnFr = np.load(rep1,allow_pickle=True);
    Lri3 = [LL[i]['filiere'] for i in Li]
    tt=[list(LEnFr).index(ii) for ii in Lri3]
    Licon=[LCorFr[i].lower()+'.png' for i in tt]
    print(Licon)
    return Lrc,Lr2,Lr3,Licon

def extra_uk(lat,lon,dism,Pmin,Pmax):
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/UKgpspro.npy'
    dism,Pmin,Pmax=int(dism),int(Pmin),int(Pmax)
    Llatlon = np.load(rep,allow_pickle=True);
    Llatlon=Llatlon.tolist()
    C5=[tuple(ii) for ii in Llatlon]
    rep1='/home/kamgoue/Sinfo/enertest2/donnees_france/UKcapa.npy'
    Capa = np.load(rep1,allow_pickle=True);
    C2=Capa.tolist()
    La0=[i for i in range(len(C5)) if (calculdist2((lat,lon),(float(C5[i][0]),float(C5[i][1])))<dism and 
                               1000*C2[i]<Pmax and 1000*C2[i]>Pmin)]
    
    La2=[calculdist2((lat,lon),(float(C5[i][0]),float(C5[i][1]))) for i in La0]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/UKnampro.npy'
    Nam=np.load(rep,allow_pickle=True);Nam=Nam.tolist()
    Lnam=[Nam[i] for i in La0]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/UKheadpro.npy'
    Head=np.load(rep,allow_pickle=True);Head=Head.tolist()
    Lhead=[Head[i] for i in La0]
    Lgps=[(float(C5[i][0]),float(C5[i][1])) for i in La0]
    Lcap=[C2[i] for i in La0]
    print(Lhead)
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/UKtypprod.npy'
    Typ = np.load(rep,allow_pickle=True);Typ=Typ.tolist()
    Ltyp = [Typ[i] for i in La0]
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/UKtyp0.npy'
    Typ0 = np.load(rep,allow_pickle=True);Typ0=Typ0.tolist()
    Ico=np.load('/home/kamgoue/Sinfo/enertest2/donnees_france/UKcorres.npy');Ico=Ico.tolist()
    Licon=[Ico[Typ0.index(Typ[i])] for i in La0]
    Lrc=[(Lgps[i],La2[i],Lnam[i],Lhead[i],Lcap[i],Ltyp[i],Licon[i]) for i in range(len(La0))]
    return Lrc

def extra_europ(lat,lon,dism,Pmin,Pmax):
    import numpy
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'DatasEU.npy'
    KK=np.load(rep1,allow_pickle=True)
    Ltt=KK.tolist()
    La0=[i for i in range(len(Ltt)) if (calculdist2((lat,lon),(Ltt[i][0][0],Ltt[i][0][1]))<dism and 
                                   1000*Ltt[i][4]<Pmax and 1000*Ltt[i][4]>Pmin and Ltt[i][0][0]>-200)]
    La2=[calculdist2((lat,lon),(Ltt[i][0][0],Ltt[i][0][1])) for i in La0]
    Lrc=[(Ltt[i][0],Ltt[i][1],Ltt[i][2],Ltt[i][4],Ltt[i][5],Ltt[i][6],Ltt[i][7],Ltt[i][8],Ltt[i][9],
         Ltt[i][10],Ltt[i][11]) for i in La0]
    Lrc2=[(Lrc[i],La2[i]) for i in range(len(La0))]
    return Lrc2

def extra_us(lat,lon,dism,Pmin,Pmax):
    import numpy
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    rep1=rep+'DatasUS.npy'
    dism,Pmin,Pmax=int(dism),int(Pmin),int(Pmax)
    KK=np.load(rep1,allow_pickle=True)
    Ltt=KK.tolist()
    La0=[i for i in range(len(Ltt)) if (calculdist2((lat,lon),(Ltt[i][0][0],Ltt[i][0][1]))<dism and 
                                   1000*Ltt[i][4]<Pmax and 1000*Ltt[i][4]>Pmin and Ltt[i][0][0]>-200)]
    La2=[calculdist2((lat,lon),(Ltt[i][0][0],Ltt[i][0][1])) for i in La0]
    Lrc=[(Ltt[i][0],Ltt[i][1],Ltt[i][2],Ltt[i][4],Ltt[i][5],Ltt[i][6],Ltt[i][7],Ltt[i][8],Ltt[i][9],Ltt[i][10]) for i in La0]
    Lrc2=[(Lrc[i],La2[i]) for i in range(len(La0))]
    return Lrc2

def put_bandeau_us(lat,lon,Lrc,page):
    import time
    rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
    LS=list(set([ii[0][4] for ii in Lrc]))
    m = folium.Map((lat, lon), zoom_start=8,control_scale=True)
    print(LS)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer('Mapbox Bright').add_to(m)
    folium.TileLayer('Mapbox Control Room').add_to(m)
    
    for iconnam in LS:
        feature_group = FeatureGroup(name=iconnam)
        for i in range(len(Lrc)):    
            if Lrc[i][0][4]==iconnam:
                name = Lrc[i][0][1]; filiere = Lrc[i][0][4]; producter = Lrc[i][0][2]; puissance  = Lrc[i][0][3];
                distance = Lrc[i][1];code = Lrc[i][0][5]; source1 = Lrc[i][0][6]; source2 = Lrc[i][0][7];
                source3 = Lrc[i][0][8];

                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;">{name}--{producter}</span></p>
                    <p style="text-align: center;font-size: 15px;">situé à: <span style="font-family: Didot, serif; font-weight: bold;">situé à: {distance}km</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Filiere: {filiere}</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;color:purple;">{puissance}Mw</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Sources: {source1}--{source2}--{source3}</span></p>

                    """, script=True)
                popup = folium.Popup(pub_html, max_width=700)
                # pp = folium.Popup(test,max_width=300)
                mk = Marker(Lrc[i][0][0],popup=popup,tooltip=Lrc[i][0][4])
                icon = folium.features.CustomIcon(rep+Lrc[i][0][9],icon_size=(25, 27))
                mk.add_child(icon)
                mk.add_to(feature_group)
            feature_group.add_to(m)
        feature_group.add_to(m)
    folium.map.LayerControl('topright', collapsed=True).add_to(m)
    m.save(os.path.join('templates', page))
    return LS

def put_bandeau_eu(lat,lon,Lrc,page):
    import time
    rep='/home/kamgoue/Sinfo/enertest2/static/images/icones_ener/'
    LS=list(set([ii[0][10] for ii in Lrc]))
    m = folium.Map((lat, lon), zoom_start=8,control_scale=True)
    print(LS)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer('Mapbox Bright').add_to(m)
    folium.TileLayer('Mapbox Control Room').add_to(m)
    
    for iconnam in LS:
        feature_group = FeatureGroup(name=iconnam[:-4])
        for i in range(len(Lrc)):    
            if Lrc[i][0][10]==iconnam:
                name = Lrc[i][0][1]; filiere = Lrc[i][0][4]; producter = Lrc[i][0][2]; puissance  = Lrc[i][0][3];
                distance = Lrc[i][1];code = Lrc[i][0][6]; source1 = Lrc[i][0][7]; source2 = Lrc[i][0][8];
                source3 = Lrc[i][0][9];

                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;">{name}--{producter}</span></p>
                    <p style="text-align: center;font-size: 15px;">situé à: <span style="font-family: Didot, serif; font-weight: bold;">situé à: {distance}km</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Filiere: {filiere}</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;color:purple;">{puissance}Mw</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Sources: {source1}--{source2}--{source3}</span></p>

                    """, script=True)
                popup = folium.Popup(pub_html, max_width=700)
                # pp = folium.Popup(test,max_width=300)
                mk = Marker(Lrc[i][0][0],popup=popup,tooltip=Lrc[i][0][5])
                icon = folium.features.CustomIcon(rep+iconnam,icon_size=(25, 27))
                mk.add_child(icon)
                mk.add_to(feature_group)
            feature_group.add_to(m)
        feature_group.add_to(m)
    folium.map.LayerControl('topright', collapsed=True).add_to(m)
    m.save(os.path.join('templates', page))
    return LS

def extrapyl_france(lat,lon,dism):
    dism = int(dism)
    lld=Deptrech(lat,lon)
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/'
    Sx=[]
    for gg in lld:
        rep1=rep+'latlonpylones'+'_'+gg+'.npy'
        Llatlon = np.load(rep1);
        Llatlon=Llatlon.tolist()
        Llatlon=[tuple(ii) for ii in Llatlon]
        Sx.extend(Llatlon)
    La=[i for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    La2=[Sx[i] for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    return La2

def extraps_france(lat,lon,dism,xll):
    dism = int(dism)
    if xll=='france':
        rep='/home/kamgoue/Sinfo/enertest2/donnees_france/pointsourceFra.npy'
        Sx = np.load(rep);
        La2=[Sx[i] for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    elif xll=='outrem':
        rep='/home/kamgoue/Sinfo/enertest2/donnees_france/pointsourceOum.npy'
        Sx = np.load(rep);
        La2=[Sx[i] for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    else:
        rep='/home/kamgoue/Sinfo/enertest2/donnees_france/pointsourceCor.npy'
        Sx = np.load(rep);
        La2=[Sx[i] for i in range(len(Sx)) if calculdist2((lat,lon),(float(Sx[i][0]),float(Sx[i][1]))) < dism]
    return La2

def extrabiom_france(lat,lon,dism,xll):
    dism = int(dism)
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/biomSource.npy'
    Biomsour = np.load(rep);
    
    La3=[F for F in Biomsour if calculdist2((lat,lon),(float(F[0]),float(F[1])))<dism]
    return La3

def extracapa_france(lat,lon,dism,xll):
    dism = int(dism)
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/Capagps.npy'
    Capaci = np.load(rep);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/CapaIntro.npy'
    Intro = np.load(rep);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/CapaRte.npy'
    Rte = np.load(rep);
    rep='/home/kamgoue/Sinfo/enertest2/donnees_france/CapaEndis.npy'
    Endis = np.load(rep);
    La4=[(Capaci[i],Intro[i],Rte[i],Endis[i]) for i in range(len(Capaci)) if calculdist2((lat,lon),(Capaci[i][0],Capaci[i][1]))<dism]

    return La4

def put_bandeau(lat,lon,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,ptc):
    import time
    rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
    LS = list(set(Licon))
    m = folium.Map((lat, lon), zoom_start=8,control_scale=True)
    print(LS)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer('Mapbox Bright').add_to(m)
    folium.TileLayer('Mapbox Control Room').add_to(m)
    
    for iconnam in LS:
        feature_group = FeatureGroup(name=iconnam[:-4])
        for i in range(len(Lrc)):    
            if Licon[i]==iconnam:
                code = Lr2[i][0]; filiere = Lr2[i][1]; puissance = Lr2[i][2];distance = Lr3[i][5]
                commune = Lr3[i][0]; dateMiseser = Lr3[i][1]; dateDebutVer = Lr3[i][2]
                tension = Lr3[i][3]; modeRacor = Lr3[i][4]

                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;">{code}</span></p>
                    <p style="text-align: center;font-size: 15px;">situé à: <span style="font-family: Didot, serif; font-weight: bold;">situé à: {distance}km</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Filiere: {filiere}</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;color:purple;">{puissance}kw</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Date mise en service: {dateMiseser}</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Date début version: {dateDebutVer}</span></p>

                    """, script=True)
                popup = folium.Popup(pub_html, max_width=700)
                # pp = folium.Popup(test,max_width=300)
                

                mk = Marker(Lrc[i],popup=popup,tooltip=Lr2[i][1])
                icon = folium.features.CustomIcon(rep+Licon[i],icon_size=(25, 27))
                mk.add_child(icon)
                mk.add_to(feature_group)
            feature_group.add_to(m)
    if ptc:
        if xll in ['corse','outrem','france']:
            feature_group = FeatureGroup(name='point source')
            for ii in La2:

                mk = Marker(location=[float(ii[0]), float(ii[1])],tooltip='point source')
                rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
                icon = folium.features.CustomIcon(rep+'postesour.png',icon_size=(25, 20))
                mk.add_child(icon)
                mk.add_to(feature_group)

            feature_group.add_to(m)
        if xll in ['corse','outrem','france']:
            feature_group = FeatureGroup(name='injection biomethane')
            rep='/home/kamgoue/Sinfo/enertest3/donnees_france/biomTyp.npy'
            Biomtyp = list(np.load(rep));
            rep='/home/kamgoue/Sinfo/enertest3/donnees_france/biomCor.npy'
            BiomCor = list(np.load(rep))
            for ii in La3:
                nom = ii[3];dista=calculdist2((lat,lon),(float(ii[0]),float(ii[1])));commune=ii[4]
                typsite = ii[2];dateMiseser = ii[5];typRes = ii[7];gest = ii[9];capacit = ii[8];
                jj=Biomtyp.index(typsite);colo=BiomCor[jj]
                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;">{nom}</span></p>
                        <p style="text-align: center;font-size: 15px;">situé à: <span style="font-family: Didot, serif; font-weight: bold;">{dista}km</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Commune: {commune}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Type: {typsite}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Date mise en service: {dateMiseser}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Type de Ressource: {typRes}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 15px;">Gestion: {gest}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;color:purple;">{capacit}Gwh/an</span></p>
                        
                        """, script=True)
                popup = folium.Popup(pub_html, max_width=700)

                mk = Marker(location=[float(ii[0]), float(ii[1])],popup=popup,tooltip=typsite)
                rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
                icon = folium.features.CustomIcon(rep+'ch42.png',icon_size=(25, 20))
                mk.add_child(icon)
                mk.add_to(feature_group)

            feature_group.add_to(m)
        if xll in ['corse','outrem','france']:
            feature_group = FeatureGroup(name='Capacité réseau')
            for ii in La4:
                nom = ii[1][0];region = ii[1][1];dista=calculdist2((lat,lon),(float(ii[0][0]),float(ii[0][1])));PEDR=ii[1][2];
                PPED=ii[1][3];CART=ii[1][4];CRET=ii[1][5];ATTE=ii[1][6];QPUA=ii[1][7];PPDS=ii[1][8];DCRS=ii[1][9];TACR=ii[1][10];
                CART2=ii[2][0];CAH2=ii[2][1];CAH1=ii[2][2];

                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 23px;font-weight: bold;">{nom} - {region}</span></p>
                        <p style="text-align: center;font-size: 15px;">situé à: <span style="font-family: Didot, serif; font-weight: bold;">{dista}km</span></p>   
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;"><u>Suivi des ENR</u></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Puissance EnR déjà raccordée: <b>{PEDR}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Puissance des projets EnR en développement: <b>{PPED}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Capacité d'accueil réservée au titre du S3REnR qui reste à affecter: <b>{CART}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Capacité réservée aux EnR au titre du S3REnR: {CRET}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Attention: la valeur de la capacité réservée a été modifiée sur ce poste: {ATTE}</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Quote-Part unitaire actualisée: <b>{QPUA}</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Puissance des projets en développement du S3REnR en cours: <b>{PPDS}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">dont la convention de raccordement est signée: <b>{DCRS}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Taux d'affectation des capacités réservées: <b>{TACR}</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;"><u>Capacité d'accueil du réseau public de transport-RTE</u></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;font-weight: bold;color:purple;">Données pour le raccordement dans le cadre du S3REnR</span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">Capacité d'accueil réservée au titre du S3REnR, disponible vue du réseau public de transport: <b>{CART2}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;font-weight: bold;color:purple;">Données pour le raccordement en dehors du S3REnR </span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">RTE - Capacité d'accueil en HTB2: <b>{CAH2}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 14px;">RTE - Capacité d'accueil en HTB1: <b>{CAH1}MW</b></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;"><u>Capacité d'accueil du réseau public de distribution :-ENEDIS</u></span></p>
                        <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;font-weight: bold;color:purple;">Données pour le raccordement dans le cadre du S3REnR</span></p>


                        """, script=True)
                popup = folium.Popup(pub_html, max_width=700)

                mk = Marker(location=[float(ii[0][0]), float(ii[0][1])],popup=popup,tooltip='capacité réseau')
                rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
                icon = folium.features.CustomIcon(rep+'capacit.png',icon_size=(20, 22))
                mk.add_child(icon)
                mk.add_to(feature_group)

            feature_group.add_to(m)
    folium.map.LayerControl('topright', collapsed=True).add_to(m)
    sleep(2)
    m.save(os.path.join('templates', page))
    return LS

def put_bandeau_uk(lat,lon,Lrc,page):
    rep='/home/kamgoue/Sinfo/enertest3/static/images/icones_ener/'
    Licon=[ii[6] for ii in Lrc]
    LS = list(set(Licon))
    m = folium.Map((lat, lon), zoom_start=8,control_scale=True)
    for iconnam in LS:
        feature_group = FeatureGroup(name=iconnam[:-4])
        for i in range(len(Lrc)):    
            if Licon[i]==iconnam:
                filiere = Lrc[i][4]; puissance = Lrc[i][3];distance = Lrc[i][1]
                nam = Lrc[i][2]; 

                pub_html = folium.Html(f"""<p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;">{nam}</span></p>
                    <p style="text-align: center;font-size: 15px;">located at: <span style="font-family: Didot, serif; font-weight: bold;">{distance}km</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 17px;">Filiere: {filiere}</span></p>
                    <p style="text-align: center;"><span style="font-family: Didot, serif; font-size: 21px;font-weight: bold;color:purple;">{puissance}Mw</span></p>

                    """, script=True)
                popup = folium.Popup(pub_html, max_width=700)
                # pp = folium.Popup(test,max_width=300)
                

                mk = Marker(Lrc[i][0],popup=popup,tooltip=Lrc[i][5])
                icon = folium.features.CustomIcon(rep+Licon[i],icon_size=(30, 35))
                mk.add_child(icon)
                mk.add_to(feature_group)
            feature_group.add_to(m)
    
    folium.map.LayerControl('topright', collapsed=True).add_to(m)
    m.save(os.path.join('templates', page))
    return LS

def put_mark(lat,lon,Lrc,Lr2,Lr3,Licon,page,La2):
    rep='/home/kamgoue/Sinfo/enertest2/static/images/icones_ener/'
    m = folium.Map((lat, lon), zoom_start=10)
    mk = features.Marker([lat, lon])
    pp = folium.Popup('Reference')
    ic = features.Icon(color='black')
    mk.add_child(ic);mk.add_child(pp);m.add_child(mk)
    for i in range(len(Lrc)):
        center = Lrc[i]
        iconam = rep+Licon[i]
        icon_url = iconam;iconp = iconam
        icon = folium.features.CustomIcon(iconp,icon_size=(30, 35))
        folium.Marker(center,popup='',icon=icon).add_to(m)
    for ii in La2:

        folium.Circle(radius=50,location=[float(ii[0]), float(ii[1])],popup="pylone",color="black",fill=False,).add_to(m)
    m.save(os.path.join('templates', page))

def Transfert(nomhtml):
    from bs4 import BeautifulSoup
    fichen = '/home/kamgoue/Sinfo/enertest3/templates/'+nomhtml
    fichsor = '/home/kamgoue/Sinfo/enertest3/templates/'+nomhtml[:-5]+'x.html'
    with open(fichen, 'r') as f:
    
        contents = f.read()
    
        soup = BeautifulSoup(contents, 'lxml')
        
        Sty = soup.find_all('style', limit=3)
        stop0 = Sty[2]
        # Scr = soup.find_all('script', limit=5)
        # scr0,scr1,scr2,scr3,scr4,scr5 = Scr[0],Scr[1],Scr[2],Scr[3],Scr[4],Scr[5]
        # Lik = soup.find_all('link', limit=6)
        # lin0,lin1,lin2,lin3,lin4,lin5 = Lik[0],Lik[1],Lik[2],Lik[3],Lik[4],Lik[5]
        Div0 = soup.find('body').div
        Scr = soup.find_all('script', limit=6)
        scr6 = Scr[5]
        
    htmldoc = '''<!DOCTYPE html>
    <!--Code By Webdevtrick ( https://webdevtrick.com )-->
    <html lang="en">
    
    <head>
     <script>
                L_NO_TOUCH = false;
                L_DISABLE_3D = false;
            </script>
        
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js"></script>
        <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css"/>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"/>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css"/>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css"/>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css"/>
        <link rel="stylesheet" href="https://rawcdn.githack.com/python-visualization/folium/master/folium/templates/leaflet.awesome.rotate.css"/>
        <link rel="stylesheet" href="{{ url_for('static', filename='listeplan.css') }}">
        <link rel="stylesheet" href="{{ url_for('static', filename='nav.css') }}">
        <meta charset="UTF-8">
        <title>Bloom-Power - Localization</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prefixfree/1.0.7/prefixfree.min.js"></script>
        <link href="https://fonts.googleapis.com/css?family=Quicksand:300,600&display=swap" rel="stylesheet">
        <style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <style>'''
    
    htmldoc2 ='''</style>
    <style>
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
        }
        
        .topnav {
            overflow: hidden;
            background-color: #333;
        }
        
        .topnav a {
            float: left;
            display: block;
            color: #f2f2f2;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
            font-size: 17px;
        }
        
        .topnav a:hover {
            background-color: #ddd;
            color: black;
        }
        
        .topnav a.active {
            background-color: #04AA6D;
            color: white;
        }
        
        .topnav .icon {
            display: none;
        }
        
        @media screen and (max-width: 600px) {
            .topnav a:not(:first-child) {
                display: none;
            }
            .topnav a.icon {
                float: right;
                display: block;
            }
        }
        
        @media screen and (max-width: 600px) {
            .topnav.responsive {
                position: relative;
            }
            .topnav.responsive .icon {
                position: absolute;
                right: 0;
                top: 0;
            }
            .topnav.responsive a {
                float: none;
                display: block;
                text-align: left;
            }
        }
    </style>
    </head>
    
    <body background="{{ url_for('static', filename='wind-power-generator-on-cloudy-day.jpg')}}">
        <div class="container-fluid">

        <div class="topnav" id="myTopnav">

            <a href="{{ url_for('index') }}">Bloom-Power</a>
            <a href="{{ url_for('datas') }}" class="active1">Datas</a>
            <a href="{{ url_for('librairies') }}" class="active2">Libraries</a>
            <ul class="nav navbar-nav navbar-right">
                {% if not session.logged_in %}
                <li><a href="{{ url_for('register') }}"><span class="glyphicon glyphicon-user"></span> Sign Up</a></li>
                <li><a href="{{ url_for('login') }}" class="active1"><span class="glyphicon glyphicon-log-in"></span> Login</a></li>
                {% else %}
                <a href="{{ url_for('upload') }}">
                    <img src="{{ url_for('static', filename=session.fich_avat)}}">
                </a>
                <a href="{{ url_for('logout') }}" class="logout">Log Out</a> {% endif %}
            </ul>
            <a href="javascript:void(0);" class="icon" onclick="myFunction()">
                <i class="fa fa-bars"></i>
            </a>
        </div>
        <br>
        <!------ Section: seeplan ------>
        <form method="post" action="{{ url_for('localizrun2') }}">
            <div class="row" style="color: #27BD99;font-size: 40px;font-weight: bold;border: none;outline: none;text-align: middle;margin-top: 1%;margin-left: 20%;">
                <div class="col-xs-12 col-sm-12 col-md-12">
                    See Plants around <u>{{ vil}} </u>
        
                </div>
            </div>
            <div class="row">
                <div class="col-xs-12 col-sm-12 col-md-12">
    
                    <input class="address1" name="address1" type="text" value="{{ vil}}" placeholder="City or Address">
                    <input class="lati1" name="lati1" type="text" value="" placeholder="Latitude">
                    <input class="longi1" name="longi1" type="text" value="" placeholder="Longitude">
                    <input style= "font-size: 20px;" class="submitadd1" type="submit" value="Search">
                   
                </div>
            </div>
            <br>
            <br>
            <br>
            <div class="row">
                <div class="col-xs-12 col-sm-12 col-md-6" style="color: #27BD99;font-weight: bold;">
                    <p style="color: #27BD99;font-weight: bold;">Power Min - Max </p>
                </div>
                <div class="col-xs-12 col-sm-12 col-md-6" style="color: #1A9CBC;font-weight: bold;">
                    <p style="color: #1A9CBC;font-weight: bold;">Maximal distance to plant </p>
                </div>
            </div>

            <div class="row">
                <div class="col-xs-12 col-sm-12 col-md-6">
                    <div slider id="slider-distance">
                        <div>
                            <div inverse-left style="width:70%;"></div>
                            <div inverse-right style="width:70%;"></div>
                            <div range style="left:30%;right:40%;"></div>
                            <span thumb style="left:30%;"></span>
                            <span thumb style="left:60%;"></span>
                            <div sign style="left:30%;">
                                <span id="value">600,000kW</span>
                            </div>
                            <div sign style="left:60%;">
                                <span id="value">1,200,000kW</span>
                            </div>
                        </div>
                        <input type="range" tabindex="0" name="Pmin" value="600000" max="2000000" min="0" step="5000" oninput="
                            this.value=Math.min(this.value,this.parentNode.childNodes[5].value-1);
                            var value=(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.value)-(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.min);
                            var children = this.parentNode.childNodes[1].childNodes;
                            children[1].style.width=value+'%';
                            children[5].style.left=value+'%';
                            children[7].style.left=value+'%';children[11].style.left=value+'%';
                            children[11].childNodes[1].innerHTML=numberFormat(this.value,',') + 'kW';" />
    
                        <input type="range" tabindex="0" name="Pmax" value="1200000" max="2000000" min="0" step="5000" oninput="
                            this.value=Math.max(this.value,this.parentNode.childNodes[3].value-(-1));
                            var value=(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.value)-(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.min);
                            var children = this.parentNode.childNodes[1].childNodes;
                            children[3].style.width=(100-value)+'%';
                            children[5].style.right=(100-value)+'%';
                            children[9].style.left=value+'%';children[13].style.left=value+'%';
                            children[13].childNodes[1].innerHTML=numberFormat(this.value,',') + 'kW';" />
                    </div>
                </div>
                <div class="col-xs-12 col-sm-12 col-md-6">
                    <div slider2 id="slider-distance">
        
                        <div>
                            <div inverse-left style="width:70%;"></div>
                            <div inverse-right style="width:70%;"></div>
                            <div range style="left:1%;right:50%;"></div>
                            <span thumb style="left:1%;"></span>
                            <span thumb style="left:50%;"></span>
                            <div sign style="left:1%;">
                                <span id="value">1km</span>
                            </div>
                            <div sign style="left:50%;">
                                <span id="value">50km</span>
                            </div>
                        </div>
                        <input type="range" tabindex="0" value="1" max="100" min="0" step="5" oninput="
                            this.value=Math.min(this.value,this.parentNode.childNodes[5].value-1);
                            var value=(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.value)-(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.min);
                            var children = this.parentNode.childNodes[1].childNodes;
                            children[1].style.width=value+'%';
                            children[5].style.left=value+'%';
                            children[7].style.left=value+'%';children[11].style.left=value+'%';
                            children[11].childNodes[1].innerHTML=numberFormat(this.value,',') + 'km';" />
        
                        <input type="range" tabindex="0" name="dmax" value="50" max="100" min="0" step="5" oninput="
                            this.value=Math.max(this.value,this.parentNode.childNodes[3].value-(-1));
                            var value=(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.value)-(100/(parseInt(this.max)-parseInt(this.min)))*parseInt(this.min);
                            var children = this.parentNode.childNodes[1].childNodes;
                            children[3].style.width=(100-value)+'%';
                            children[5].style.right=(100-value)+'%';
                            children[9].style.left=value+'%';children[13].style.left=value+'%';
                            children[13].childNodes[1].innerHTML=numberFormat(this.value,',') + 'km';" />
                    </div>
                </div>
            </div>
        </form>
        <br>
        <br>
        <br>
        <div class="row" style="margin-left: 2%;">
            {%for i in range(0, len3)%}
                <div class="col-xs-3 col-sm-2 col-md-1" style="background-color: #1ABC9C; border-radius: 15px;font-size: 16px;">
                    {% if Licon[i] == 'images/icones_ener/bioenergy.png' %}
                        <center><a href="{{ url_for('runbioenergy') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/biomass.png' %}
                        <center><a href="{{ url_for('runbiomass') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/coal.png' %}
                        <center><a href="{{ url_for('runcoal') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/cogeneration.png' %}
                        <center><a href="{{ url_for('runcogeneration') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/fuel.png' %}
                        <center><a href="{{ url_for('runfuel') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/gas.png' %}
                        <center><a href="{{ url_for('rungas') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/geothermal.png' %}
                        <center><a href="{{ url_for('rungeothermal') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/hydraulic.png' %}
                        <center><a href="{{ url_for('runhydraulic') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/hydro.png' %}
                        <center><a href="{{ url_for('runhydraulic') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/lignite.png' %}
                        <center><a href="{{ url_for('runlignite') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/marine.png' %}
                        <center><a href="{{ url_for('runmarine') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/naturgas.png' %}
                        <center><a href="{{ url_for('runnaturgas') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/nrw.png' %}
                        <center><a href="{{ url_for('runnrw') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/nuclear.png' %}
                        <center><a href="{{ url_for('runnuclear') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/ofossil.png' %}
                        <center><a href="{{ url_for('runofossil') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/ofuel.png' %}
                        <center><a href="{{ url_for('runofuel') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/oil.png' %}
                        <center><a href="{{ url_for('runoil') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/others.png' %}
                        <center><a href="{{ url_for('runothers') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/petcoke.png' %}
                        <center><a href="{{ url_for('runpetcoke') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/rwas.png' %}
                        <center><a href="{{ url_for('runrwas') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/solar.png' %}
                        <center><a href="{{ url_for('runsolar') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/storage.png' %}
                        <center><a href="{{ url_for('runstorage') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/thermal.png' %}
                        <center><a href="{{ url_for('runthermal') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/unknow.png' %}
                        <center><a href="{{ url_for('rununknow') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/waste.png' %}
                        <center><a href="{{ url_for('runwaste') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}"  style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    {% if Licon[i] == 'images/icones_ener/wind.png' %}
                        <center><a href="{{ url_for('runwind') }}" class="active1"><img src="{{url_for('static', filename=Licon[i])}}" style="margin-top: 5%; width: 30%; height: 30%;" /></a></center>
                    {% endif %}
                    
                </div>
            {%endfor%}
            <div class="col-xs-3 col-sm-2 col-md-1" style="background-color: #FA119C;color: #000000; border-radius: 15px;font-size: 16px;">
                <center><a href="{{ url_for('runcsv') }}" class="active1">Get csv</a></center>
            </div>
        </div>
        <br>
        <br>
        <br>
        <br>
        <div style="display: grid; height: 1000px; grid-template-columns: 35% 65%; grid-template-rows: 100%; column-gap: 0.125%;">
    	    <div style="overflow: scroll">

                {%for i in range(0, len1)%}
                    <div style="display: grid; height: 10%; grid-template-columns: repeat(1, 1fr); grid-template-rows: 100%; border-radius: 15px; column-gap: 0.125%;">
                        {%for j in range(0, 1)%}
                            <div>
                                <div style="display: grid; margin-left: 10%; margin-right: 10%; background-color: white; border-radius: 15px; height: 100%; grid-template-columns: repeat(3, 1fr); grid-template-rows: 100%; column-gap: 0.125%;">
                                    <div style="display: grid; background-color: #1ABC9C; margin-right: 20%; border-radius: 15px;">
                                    <center>
                                        <img src="{{url_for('static', filename=Licon2[i])}}" />
                                       </center> 
                                    </div>
                                    <div style="font-size: 8px;">
                                        <h6>{{Lss[i][0]}}</h6>
                                        <h6>{{Lss[i][1]}}</h6>
                                        <h6>{{Lss[i][2]}}</h6>
                                        
                                    </div>
                                    <div>
                                        <br>
                                        <a href="{{ url_for('datas') }}" style="background: #27BD99;font-size: 16px;
                                        color: white;border-radius: 10px;">&nbsp;&nbsp;Select&nbsp;&nbsp;</a>
                                        <br>
                                        <br>
                                        <h5><b>{{Lss[i][3]}}MW</b></h5>
                                    </div>
                                </div>
                            </div>
                        {%endfor%}
                    </div>
                    <br>
                    <br>
                {%endfor%}
         
    	    </div>'''
    
    htmldoc3 = '''        </div>
    
        
        
        <script type="text/javascript">
            function numberFormat(_number, _sep) {
                _number = typeof _number != "undefined" && _number > 0 ? _number : "";
                _number = _number.replace(new RegExp("^(\\d{" + (_number.length % 3 ? _number.length % 3 : 0) + "})(\\d{3})", "g"), "$1 $2").replace(/(\d{3})+?/gi, "$1 ").trim();
                if (typeof _sep != "undefined" && _sep != " ") {
                    _number = _number.replace(/\s/g, _sep);
                }
                return _number;
            }
        </script>
        
        
        </div>
    </body>
    
    <script> '''
    
    
    
    hint = '<div class="'+Div0['class'][0]+'" id="'+Div0['id']+'"></div>'
    hfin = ''' </script>
    
    </html>'''
    htmldoc2 = htmldoc + stop0.text + htmldoc2 + hint + htmldoc3 + scr6.text + hfin
    fich0 = nomhtml[:-5]+'x.html';
    
    with open(fichsor, 'w') as fp:
            fp.write(htmldoc2)
    return fich0

# lat=50.632557;lon=5.579666
# isfranceouteur2(lat,lon)
# addr = '';
# city='guadeloupe';country='france';dmax=100
# runbig_oum(addr,city,country,dmax,'test.html')