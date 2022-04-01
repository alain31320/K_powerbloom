from time import sleep
import datetime
import csv, shutil
import fileinput
import sqlite3
import os, random
import numpy as np
from flask import Flask, render_template, request, url_for, flash, redirect, session, send_from_directory, jsonify
from werkzeug.exceptions import abort
from csv452 import Localiser
from time import gmtime, strftime
from flask_avatars import Avatars
from geopypvlib42 import createtmy
from pvmodelize import modelize

basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

hh=['two-smoking-energy-towers-in-the-sunset.jpg','wind-power-generator-on-cloudy-day.jpg','wind-turbine-s-used-to-create-energy.jpg']
imag = random.choice(hh)
print(imag)
# ------------Avatar-------------------------
app.config['AVATARS_SAVE_PATH'] = os.path.join(basedir, 'avatars')
avatars = Avatars(app)

@app.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        raw_filename = avatars.save_avatar(f)
        session['raw_filename'] = raw_filename  # you will need to store this filename in database in reality
        return redirect(url_for('crop'))
    return render_template('upload.html')

@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        x = request.form.get('x')
        y = request.form.get('y')
        w = request.form.get('w')
        h = request.form.get('h')
        filenames = avatars.crop_avatar(session['raw_filename'], x, y, w, h)
        url_s = url_for('get_avatar', filename=filenames[0]) 
        url_m = url_for('get_avatar', filename=filenames[1])
        session['fich_avat'] = url_m
        url_l = url_for('get_avatar', filename=filenames[2])

        r = csv.reader(open('users.csv')) # Here your csv file
        lines = list(r)
        for row in lines:
            if row[0] == session['email']:
                curr = os.getcwd()
                chem = curr+url_m
                row[2] = url_m
                newPath = shutil.copy(chem, curr+'/static/avatars')
        writer = csv.writer(open('users.csv', 'w'))
        writer.writerows(lines)
        return render_template('done.html', url_s=url_s, url_m=url_m, url_l=url_l)
    return render_template('crop.html')

@app.route('/register', methods=["GET", "POST"])
def register():

    errors = ''
    return render_template('register.html',imag=imag)

@app.route('/register0', methods=["GET", "POST"])
def register0():

    hh=os.listdir('./static/images')
    imag = random.choice(hh)
    imag = 'images/' + imag

    if not session.get('logged_in'):
        email = request.form.get('email');passw = request.form.get('passw1');
        avat = 'avatars/' + 'default_s.jpg'
        user = [email,passw,avat]
        Lu = []; Lm = [];
        with open('users.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                Lu.append(row[0]);Lm.append(row[1]);
        if email in Lu:
            if passw in Lm:
                session['errors'] = "Ce compte avec ce mot de passe a déja été créé"
                session['logged_in'] = True
                session['fich_avat'] = avat
                session['email'] = email
                return render_template('index.html',imag=imag)
            else:
                session['errors'] = "Ce compte existe mais le mot de passe ne correspond pas"
                session['logged_in'] = False
                return render_template('index.html',imag=imag)
        else:        
            with open(r'users.csv', 'a', newline='') as csvfile:
                fieldnames = ['email','passw','avat']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'email':email, 'passw':passw, 'avat':avat})
            print(email)
            session['logged_in'] = True
            session['fich_avat'] = avat
            session['errors'] = "you are registred"
            session['email'] = email
            print(session.get('logged_in'))
            return render_template('index.html',imag=imag)
    else:
        return render_template('index.html',imag=imag)

@app.route('/login', methods=["GET", "POST"])
def login():

    return render_template('login.html',imag=imag)

@app.route('/login0', methods=["GET", "POST"])
def login0():

    email = request.form.get('email');passw = request.form.get('password');
    Lu = []; Lm = []; Lv = [];
    with open('users.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            Lu.append(row[0]);Lm.append(row[1]);Lv.append(row[2]);
    if email in Lu:
        ii = Lu.index(email)
        if passw == Lm[ii]:
            session['logged_in'] = True
            session['fich_avat'] = Lv[ii]
            session['errors'] = "you are login"
            session['email'] = email
            return render_template('index.html',imag=imag)
        else:
            session['logged_in'] = False
            session['errors'] = "bad password"
            return render_template('index.html',imag=imag)
    else:
        session['logged_in'] = False
        session['errors'] = "The account doesn't exist"
        return render_template('index.html',imag=imag)

@app.route("/logout")
def logout():

    session['logged_in'] = False
    session['errors'] = ""
    print(session.get('logged_in'))
    errors = ''
    return redirect(url_for('index'))


# ------------Index-------------------------
@app.route('/index')
@app.route('/')
def index():
    if 'response' not in session:
        session['logged_in'] = False
    session['runbioenergy'],session['runbiomass'],session['runcoal'] = True,True,True
    session['runcogeneration'],session['runfuel'],session['rungas'] = True,True,True
    session['rungeothermal'],session['runhydraulic'],session['runlignite'] = True,True,True
    session['runmarine'],session['runnaturgas'],session['runnrw'] = True,True,True
    session['runnuclear'],session['runofossil'],session['runofuel'] = True,True,True
    session['runoil'],session['runothers'],session['runpetcoke'] = True,True,True
    session['runrwas'],session['runsolar'],session['runstorage'] = True,True,True
    session['runthermal'],session['rununknow'],session['runwaste'] = True,True,True
    session['runwind'],session['rununknow'],session['runwaste'] = True,True,True
    return render_template('index.html')
# --------------------------------------------------
# ------------Datas-----------------------------
# --------------------------------------------------
@app.route('/datas')
def datas():
    from modul2 import Tranchlist
    Lu = [];
    if session['logged_in']:
        with open('lastsearch.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if row[0] == session['email']:
                    Lu.append([row[0],row[1],row[2],row[3],row[4]])
        Lu2 = Tranchlist(Lu,3)
        session['last']=Lu2

    return render_template('datas.html')

@app.route('/localizrun', methods=["GET", "POST"])
def localizrun():
    import os
    from modul2 import isfranceouteur2,getlatlon,extra_outre,extra_corse,extrapyl_france,extra_france,put_mark
    from modul2 import put_bandeau, extra_europ, extraps_france, extrabiom_france, extracapa_france
    from modul2 import extra_uk, put_bandeau_uk, put_bandeau_eu,extra_us,put_bandeau_us, Transfert
    
    address = request.form.get('address')
    longi = request.form.get('longi');lati = request.form.get('lati');
    print(len(address));print(len(lati));print(len(longi));

    if (len(lati)>0 and len(longi)>0):
        lati=float(lati);longi=float(longi);
        vil = str(lati) + '---'+str(longi)
    else:
        ll=getlatlon(address);lati=ll[0];longi=ll[1]
        vil = address
    
    xll = isfranceouteur2(lati,longi)
    # J'ai fixé les valeurs: france outrem corse et unitedkingdom pour xll
    hh=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    page = 'result_'+hh[0:4] + '_' + hh[5:7] + '_' + hh[8:10] + '_' + hh[11:13] + '_' + hh[14:16] + '_' + hh[17:19]+'.html'
    dmax,Pmin,Pmax = '50','10000','100000000'
    if xll=='corse':
        Lrc,Lr2,Lr3,Licon = extra_corse(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='outrem':
        Lrc,Lr2,Lr3,Licon = extra_outre(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='france':
        Lrc,Lr2,Lr3,Licon = extra_france(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)

    elif xll=='unitedkingd':
        Lrc = extra_uk(lati,longi,dmax,Pmin,Pmax)
        print(Lrc)
        Lss,Licon2 = [(Lrc[i][2],Lrc[i][0],Lrc[i][5],"%.2f" % float(Lrc[i][4])) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][6][:-4]+'64.png' for i in range(len(Lrc))]
        print(Licon2)
        List_icon = put_bandeau_uk(lati,longi,Lrc,page)

    else:
        Lrc = extra_us(lati,longi,dmax,Pmin,Pmax)
        Lss,Licon2 = [(Lrc[i][0][1],Lrc[i][0][0],Lrc[i][0][4],"%.2f" % float(Lrc[i][0][3])) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][0][9][:-4]+'64.png' for i in range(len(Lrc))]
        List_icon = put_bandeau_us(lati,longi,Lrc,page)
        List_icon = [ii.lower()+'.png' for ii in List_icon]
    
    fichxx = Transfert(page)
    print(fichxx)
    print(Lss)
    len1 = len(Lss)//1;len2 = len(Lss)%1;
    print((len1,len2))
    sleep(2)
    print(List_icon)
    List_icon = ['images/icones_ener/' + ii for ii in List_icon]
    len3 = len(List_icon)
    if session['logged_in']:
        with open(r'lastsearch.csv', 'a', newline='') as csvfile:
            fieldnames = ['email','ville','puimin','puimax','dist']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'email':session['email'], 'ville':address, 'puimin':Pmin,'puimax':Pmax, 'dist':dmax})

    return render_template(fichxx,vil=vil,len1 = len1, len2 = len2, len3 = len3,
                             Lss = Lss, Licon = List_icon, Licon2 = Licon2)

@app.route('/localiz/<ville>/<puimin>/<puimax>/<dist>')
def localiz(ville=None, puimin=None, puimax=None, dist=None):
    import os
    from modul2 import isfranceouteur2,getlatlon,extra_outre,extra_corse,extrapyl_france,extra_france,put_mark
    from modul2 import put_bandeau, extra_europ, extraps_france, extrabiom_france, extracapa_france
    from modul2 import extra_uk, put_bandeau_uk, put_bandeau_eu,extra_us,put_bandeau_us, Transfert
    
    ll=getlatlon(ville);lati=ll[0];longi=ll[1]
    vil = ville
    
    xll = isfranceouteur2(lati,longi)
    # J'ai fixé les valeurs: france outrem corse et unitedkingdom pour xll
    hh=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    page = 'result_'+hh[0:4] + '_' + hh[5:7] + '_' + hh[8:10] + '_' + hh[11:13] + '_' + hh[14:16] + '_' + hh[17:19]+'.html'
    dmax,Pmin,Pmax = str(dist),str(puimin),str(puimax)
    if xll=='corse':
        Lrc,Lr2,Lr3,Licon = extra_corse(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='outrem':
        Lrc,Lr2,Lr3,Licon = extra_outre(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='france':
        Lrc,Lr2,Lr3,Licon = extra_france(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)

    elif xll=='unitedkingd':
        Lrc = extra_uk(lati,longi,dmax,Pmin,Pmax)
        print(Lrc)
        Lss,Licon2 = [(Lrc[i][2],Lrc[i][0],Lrc[i][5],"%.2f" % float(Lrc[i][4])) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][6][:-4]+'64.png' for i in range(len(Lrc))]
        print(Licon2)
        List_icon = put_bandeau_uk(lati,longi,Lrc,page)

    else:
        Lrc = extra_us(lati,longi,dmax,Pmin,Pmax)
        Lss,Licon2 = [(Lrc[i][0][1],Lrc[i][0][0],Lrc[i][0][4],"%.2f" % float(Lrc[i][0][3])) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][0][9][:-4]+'64.png' for i in range(len(Lrc))]
        List_icon = put_bandeau_us(lati,longi,Lrc,page)
        List_icon = [ii.lower()+'.png' for ii in List_icon]
    
    fichxx = Transfert(page)
    print(fichxx)
    print(Lss)
    len1 = len(Lss)//1;len2 = len(Lss)%1;
    print((len1,len2))
    sleep(2)
    print(List_icon)
    List_icon = ['images/icones_ener/' + ii for ii in List_icon]
    len3 = len(List_icon)

    return render_template(fichxx,vil=vil,len1 = len1, len2 = len2, len3 = len3,
                             Lss = Lss, Licon = List_icon, Licon2 = Licon2)

@app.route('/localizrun2', methods=["GET", "POST"])
def localizrun2():
    import os
    from modul2 import isfranceouteur2,getlatlon,extra_outre,extra_corse,extrapyl_france,extra_france,put_mark
    from modul2 import put_bandeau, extra_europ, extraps_france, extrabiom_france, extracapa_france
    from modul2 import extra_uk, put_bandeau_uk, put_bandeau_eu,extra_us,put_bandeau_us, Transfert
    
    address1 = request.form.get('address1')
    longi1 = request.form.get('longi1');lati1 = request.form.get('lati1');dmax = request.form.get('dmax');
    Pmin = request.form.get('Pmin'); # Pmin = 1000*float(Pmin);
    Pmax = request.form.get('Pmax'); # Pmax = 1000*float(Pmax);
    print(address1);print(Pmin);print(Pmax);print(dmax);

    if (len(lati1)>0 and len(longi1)>0):
        lati=float(lati1);longi=float(longi1);
        vil = str(lati) + '---'+str(longi)
    else:
        ll=getlatlon(address1);lati=ll[0];longi=ll[1]
        vil = address1
    
    xll = isfranceouteur2(lati,longi)
    # J'ai fixé les valeurs: france outrem corse et unitedkingdom pour xll
    hh=strftime("%Y-%m-%d %H:%M:%S", gmtime())
    page = 'result_'+hh[0:4] + '_' + hh[5:7] + '_' + hh[8:10] + '_' + hh[11:13] + '_' + hh[14:16] + '_' + hh[17:19]+'.html'
    # dmax,Pmin,Pmax = '50','10000','100000000'
    if xll=='corse':
        Lrc,Lr2,Lr3,Licon = extra_corse(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % float(Lr2[i][2])/1000) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='outrem':
        Lrc,Lr2,Lr3,Licon = extra_outre(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % float(Lr2[i][2])/1000) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)
    elif xll=='france':
        Lrc,Lr2,Lr3,Licon = extra_france(lati,longi,dmax,Pmin,Pmax)
        La2 = extraps_france(lati,longi,dmax,xll)
        La3 = extrabiom_france(lati,longi,dmax,xll)
        La4 = extracapa_france(lati,longi,dmax,xll)
        Lss,Licon2 = [(Lr2[i][0],Lr3[i][0],Lr2[i][1],"%.2f" % (float(Lr2[i][2])/1000)) for i in range(len(Lr3))],['images/icones_ener/'+gg[:-4]+'64.png' for gg in Licon]
        List_icon = put_bandeau(lati,longi,Lrc,Lr2,Lr3,Licon,page,La2,La3,La4,xll,False)

    elif xll=='unitedkingd':
        Lrc = extra_uk(lati,longi,dmax,Pmin,Pmax)
        print(Lrc)
        Lss,Licon2 = [(Lrc[i][2],Lrc[i][0],Lrc[i][5],"%.2f" % float(Lrc[i][4])) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][6][:-4]+'64.png' for i in range(len(Lrc))]
        List_icon = put_bandeau_uk(lati,longi,Lrc,page)

    else:
        Lrc = extra_us(lati,longi,dmax,Pmin,Pmax)
        print(Lrc)
        Lss,Licon2 = [(Lrc[i][0][1],Lrc[i][0][0],Lrc[i][0][4],Lrc[i][0][3]) for i in range(len(Lrc))],['images/icones_ener/'+Lrc[i][0][9][:-4]+'64.png' for i in range(len(Lrc))]
        List_icon = put_bandeau_us(lati,longi,Lrc,page)
        List_icon = [ii.lower()+'.png' for ii in List_icon]
    
    fichxx = Transfert(page)
    print(fichxx)
    print(Lss)
    len1 = len(Lss)//1;len2 = len(Lss)%1;
    print((len1,len2))
    sleep(2)
    print(List_icon)
    List_icon = ['images/icones_ener/' + ii for ii in List_icon]
    len3 = len(List_icon)
    if session['logged_in']:
        with open(r'lastsearch.csv', 'a', newline='') as csvfile:
            fieldnames = ['email','ville','puimin','puimax','dist']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'email':session['email'], 'ville':address1, 'puimin':Pmin,'puimax':Pmax, 'dist':dmax})
    return render_template(fichxx,vil=vil,len1 = len1, len2 = len2, len3 = len3,
                             Lss = Lss, Licon = List_icon, Licon2 = Licon2)

# --------------------------------------------------
# ------------Librairies-----------------------------
# ---------------------------------------------------
@app.route('/librairies')
def librairies():
    hh=os.listdir('./static/images')
    imag = "hari-nandakumar-dZUUaXSB-9Q-unsplash.jpg"
    imag = 'images/' + imag

    return render_template('librairies2.html',imag=imag)
# --------------------------------------------------
# ------------Optimize-----------------------------
# ---------------------------------------------------
@app.route('/optimize')
def optimize():
    hh=os.listdir('./static/images')
    imag = "hari-nandakumar-dZUUaXSB-9Q-unsplash.jpg"
    imag = 'images/' + imag

    return render_template('librairies2.html',imag=imag)

@app.route('/runbioenergy')
def runbioenergy():
    if session['runbioenergy']:
        session['runbioenergy']=False
    else:
        session['runbioenergy']=True

    return render_template('datas.html')

@app.route('/runbiomass')
def runbiomass():

    return render_template('datas.html')

@app.route('/runcoal')
def runcoal():

    return render_template('datas.html')

@app.route('/runcogeneration')
def runcogeneration():

    return render_template('datas.html')

@app.route('/runfuel')
def runfuel():

    return render_template('datas.html')

@app.route('/rungas')
def rungas():

    return render_template('datas.html')

@app.route('/rungeothermal')
def rungeothermal():

    return render_template('datas.html')

@app.route('/runhydraulic')
def runhydraulic():

    return render_template('datas.html')

@app.route('/runlignite')
def runlignite():

    return render_template('datas.html')

@app.route('/runmarine')
def runmarine():

    return render_template('datas.html')

@app.route('/runnaturgas')
def runnaturgas():

    return render_template('datas.html')

@app.route('/runnrw')
def runnrw():

    return render_template('datas.html')

@app.route('/runnuclear')
def runnuclear():

    return render_template('datas.html')

@app.route('/runofossil')
def runofossil():

    return render_template('datas.html')

@app.route('/runofuel')
def runofuel():

    return render_template('datas.html')

@app.route('/runoil')
def runoil():

    return render_template('datas.html')

@app.route('/runothers')
def runothers():

    return render_template('datas.html')

@app.route('/runpetcoke')
def runpetcoke():

    return render_template('datas.html')

@app.route('/runrwas')
def runrwas():

    return render_template('datas.html')

@app.route('/runsolar')
def runsolar():

    return render_template('datas.html')

@app.route('/runstorage')
def runstorage():

    return render_template('datas.html')

@app.route('/runthermal')
def runthermal():

    return render_template('datas.html')

@app.route('/rununknow')
def rununknow():

    return render_template('datas.html')

@app.route('/runwaste')
def runwaste():

    return render_template('datas.html')

@app.route('/runwind')
def runwind():

    return render_template('datas.html')

@app.route('/runcsv')
def runcsv():

    return render_template('datas.html')