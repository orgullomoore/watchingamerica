import urllib.request
from urllib.error import  URLError
import urllib
import codecs
import time
import re
currtimestr=''
currtime=time.gmtime()
for i in currtime[:6]:
    currtimestr+=str(i)
logName='Log-'+currtimestr+'.html'
def fetchURL(someurl):
    print('Fetching '+someurl)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    
    try:
        response = opener.open(someurl)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
    else:
        # everything is fine
        result='ok'
        return response
threshold=0 #num of hits needed to merit a log entry
def hitcounter(sourcetext):
    palabrasclave=[]
    pcfile = codecs.open('palabrasclave.txt', 'r', 'utf8')
    pctext = pcfile.read()
    pcfile.close()
    chuleta=pctext.split('\n')
    for chu in chuleta:
        palabrasclave.append(chu.rstrip())
    for palabra in palabrasclave:
        if len(palabra)<3:
            palabrasclave.remove(palabra)
    count=0
    desc=''
    for palabra in palabrasclave:
        if palabra in sourcetext:
            pccount=sourcetext.count(palabra)
            count+=pccount
            desc+=palabra+' ('+str(pccount)+'); '
    return (count, desc)
def startLog():
    towrite="""

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>Spanish articles most likely to be about America</title>
  <meta http-le="" equiv="Content-Type"
 content="text/html">
  <meta charset="utf-8">
  <script type="text/javascript"
 src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
</head>
<body>
<table class="sortable">
  <thead><tr>
    <th class="">Title</th>
    <th class="">Hits</th>
    <th class="">Source</th>
    <th class="">Date</th>
    <th class="">Author</th>
    <th class="">Desc</th>
  </tr>
  </thead> <tbody>

"""
    logfile=codecs.open(logName, 'w', 'utf8')
    logfile.write(towrite)
    logfile.close()
def logRow(data):
    #title, hits, source, date, author
    towrite='<tr>'
    for d in data:
        towrite+='<td>'+d+'</td>'
    towrite+='</tr>'
    logfile=codecs.open(logName, 'a', 'utf8')
    logfile.write(towrite)
    logfile.close()
def endLog():
    towrite="""
  </tbody><tfoot></tfoot>
</table>
</body>
</html>
    """
    logfile=codecs.open(logName, 'a', 'utf8')
    logfile.write(towrite)
    logfile.close()

def translateMonth(spanishdate):
    toreturn=spanishdate.lower()
    #separate dic for abbreviation must go last to avoid 06io and 07io for example 
    monthabbs={'ene': '01',
              'feb': '02',
              'mar': '03',
              'abr': '04',
              'may': '05',
              'jun': '06',
              'jul': '07',
              'ago': '08',
              'sep': '09',
              'oct': '10',
              'nov': '11',
              'dic': '12'
               }
    monthdic={'enero': '01',
              'febrero': '02',
              'marzo': '03',
              'abril': '04',
              'mayo': '05',
              'junio': '06',
              'julio': '07',
              'agosto': '08',
              'septiembre': '09',
              'octubre': '10',
              'noviembre': '11',
              'diciembre': '12',
              }
    for month in monthdic:
        if month in toreturn:
            toreturn=toreturn.replace(month, monthdic[month])
    for abb in monthabbs:
        if abb in toreturn:
            toreturn=toreturn.replace(abb, monthabbs[abb])
    return toreturn

#######BEGIN INDIVIDUAL PUBS
              
###clarin
def claringenerator(maxnumber=10):
    listofurls=[]
    caturl='http://www.clarin.com/opinion/'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<ul class="items" id="listadoautomatico')[1]
    relchunk=relchunk.split('<div id="getMoreNotesContainer')[0]
    chops=relchunk.split('<li class="item">')
    for chop in chops[1:]:
        urlterminus=chop.split('<a href="')[1].split('"')[0]
        urlinicius='http://www.clarin.com'
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=clarinreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def clarinreader(url):
    source='Clarín (AR)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div class="nota">')
    actualtext=actualtext[1].split('<!--|googlemap|-->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split("_sf_async_config.authors = '")[1].split("'")[0]
    author=authorsnip.strip()[:25] #the pub does not separate authors from their titles
    datesnip=bulktext.split('<div class="breadcrumb">')[1].split('</ul>')[0]
    datesnip=datesnip.split('<li>')[-1].split('</li>')[0].strip()
    date=time.strftime("%Y%m%d", time.strptime(datesnip, "%d/%m/%y"))
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end clarin

###elcomercioPE
def elcomercioPEgenerator(maxnumber=10):
    listofurls=[]
    caturl='http://elcomercio.pe/opinion/columnistas'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<section class="box-resultados">')[1]
    relchunk=relchunk.split('</section>')[0]
    chops=relchunk.split('<article class="f-result')
    for chop in chops[1:]:
        urlterminus=chop.split('<h2><a href="')[-1].split('"')[0]
        urlterminus=urlterminus.split('?')[0] #we dont need variables
        urlinicius=''
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=elcomercioPEreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def elcomercioPEreader(url):
    source='El Comercio (PE)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div class="txt-nota" itemprop="articleBody">')
    actualtext=actualtext[1].split('<div class="tags">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split("""<meta property="og:title" content='""")[1]
    titlesnip=titlesnip.split("'")[0]
    author=''
    try:
        titlesnip=titlesnip.split(', por ')[0] # pub includes author in title
        author=titlesnip.split(', por ')[1]
    except:
        titlesnip=titlesnip
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    if author=='':
        try:
            author=bulktext.split('<li class="autor">')[1].split('</li>')[0]
        except:
            author='None found.'
    author=author.strip()
    datesnip=bulktext.split('<meta name="bi3dPubDate" content="')[1].split(' ')[0]
    datesnip=datesnip.replace('-', '')
    date=datesnip.strip()
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end elcomercioPE

###elespectador
def elespectadorgenerator(maxnumber=10):
    listofurls=[]
    caturl='http://www.elespectador.com/opinion'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<!--Inicio Columnistas del dia-->')[1]
    relchunk=relchunk.split('<!--Fin Columnistas del dia-->')[0]
    chops=relchunk.split('<div class="una_noticia">')
    for chop in chops[1:]:
        urlterminus=chop.split('<h2>')[-1].split(' href="')[1].split('"')[0]
        urlinicius='http://www.elespectador.com'
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=elespectadorreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def elespectadorreader(url):
    source='El Espectador (CO)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div class="content_nota">')
    actualtext=actualtext[1].split('<div class="paginacion">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<h5 class="columnista_nombre">Por: ')[1].split('</h5>')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split('<meta name="cXenseParse:recs:publishtime" content="')[1].split('T')[0]
    datesnip=datesnip.replace('-', '')
    date=datesnip.strip()
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end elespectador


###elmercurio
def elmercuriogenerator(maxnumber=9):
    listofurls=[]
    caturl='http://www.elmercurio.com/blogs/'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<!-- COLUMNA IZQUIERDA -->')[1]
    relchunk=relchunk.split('<!-- END COLUMNA IZQUIERDA -->')[0]
    chops=relchunk.split('<li id="NoticiaColumnista')
    urlinicius='http://www.elmercurio.com'
    for chop in chops[1:]:
        urlterminus=chop.split('<div class="titulo_box_home"')[1].split('<a href="')[1].split('"')[0]
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    featuredurl=catpage.split('<div id="content_destacado_home"')[1].split('<a href="')[1].split('"')[0]
    featuredurl=urlinicius+featuredurl
    listofurls.append(featuredurl)
    for url in listofurls[:maxnumber]:
        parsethis=elmercurioreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def elmercurioreader(url):
    source='El Mercurio (CL)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div class="content_info_despliegue" id="CajaCuerpo">')
    actualtext=actualtext[1].split('<div class="contenedor-paginacion-medios-inf-blog">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<h1 class="titulo_despliegue_nota">')[1].split('</h1>')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    try:
        authorsnip=bulktext.split('<div class="txt_autor">')[1].split('</a>')[0].split('>')[-1]
        author=authorsnip.strip()
    except:
        author='None found.'
    datesnip=bulktext.split('<div class="fecha_despliegue_nota">')[1].split('</div>')[0]
    datesnipdiv=datesnip.split(' ')
    day=datesnipdiv[1]
    year=datesnipdiv[5]
    month=translateMonth(datesnipdiv[3])
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end elmercurio


###elnacional
def elnacionalgenerator():
    listofurls=[]
    caturl='http://www.el-nacional.com/opinion/'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<!-- PAGE MAIN (AREA) -->')[1]
    relchunk=relchunk.split('<!-- AUX LISTING ITEMS -->')[0]
    urlregexmain=r'<h2 class="entry-title"><a class="lnk" href="(\S+)">.+</a></h2>'
    urlregexfeat=r'<a href="(\/opinion\/\S+)" class="lnk".*>.+</a>'
    listofurls+=re.findall(urlregexmain, relchunk)
    listofurls+=re.findall(urlregexfeat, relchunk)
    listofurls=set(listofurls)
    for url in listofurls:
        if not url.startswith('http://'):
            url='http://www.el-nacional.com'+url
        parsethis=elnacionalreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def elnacionalreader(url):
    source='El Nacional (VE)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<!-- MCE BODY CONTENT -->')
    actualtext=actualtext[1].split('<!-- END: PAGE BODY -->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<title>')[1].split('</title>')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<link rel="alternate" title="')[1].split('"')[0]
    author=authorsnip.strip()
    datere=r'<small class="dateline"><span id="clock" class="time" style="color: white">.+</span>&nbsp;&nbsp;(\d{2}) de ([A-Z][a-z]+) de (\d{4})</small>'
    datesnipdiv=re.findall(datere, bulktext)[0]
    day=datesnipdiv[0]
    month=translateMonth(datesnipdiv[1].lower())
    year=datesnipdiv[2]
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end elnacional


###elpais
def elpaisgenerator(maxnumber=20):
    listofurls=[]
    caturl='http://elpais.com/elpais/opinion.html'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<div class="caja opinion">')[1]
    relchunk=relchunk.split('<div class="columna_secundaria">')[0]
    chops=relchunk.split('title="Ver noticia">')
    for chop in chops[:-1]:
        urlinicius='http://elpais.com'
        chopdiv=chop.split('\n')[-1]
        urlterminus=chopdiv.split('<a href="')[1].split('"')[0]
        if urlterminus.startswith('http://'):
            urlinicius=''
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=elpaisreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def elpaisreader(url):
    source='El País (ES)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div id="cuerpo_noticia" class="cuerpo_noticia">')
    actualtext=actualtext[1].split('<div class="envoltorio_publi estirar">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<span class="autor">')[1].split('</a></span>')[0].split('>')[-1]
    author=authorsnip.strip()
    datesnip=bulktext.split('<meta name="DC.date" scheme="W3CDTF" content="')[1].split('"')[0]
    datesnip=datesnip.replace('-', '')
    date=datesnip.strip()
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end elpais


###eltiempo
def eltiempogenerator(maxnumber=7):
    listofurls=[]
    caturl='http://www.eltiempo.com/opinion'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<section class="mod_columnistas modulo">')[1]
    relchunk=relchunk.split('<!-- End column a -->')[0]
    chops=relchunk.split('<article class="articulo_columnistas">')
    urlinicius='http://eltiempo.com'
    for chop in chops[1:]:
        urlterminus=chop.split('<h2><a href="')[1].split('"')[0]
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=eltiemporeader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def eltiemporeader(url):
    source='El Tiempo (CO)'
    bulktext=fetchURL(url).read().decode('utf8')
    actualtext=bulktext.split('<div class="cuerpo_texto" itemprop="articleBody">')
    actualtext=actualtext[1].split('<footer class="footer-article">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<h2 itemprop="name">')[1].split('</h2>')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<h3 class="creditos">')[1].split('</a></h3>')[0].split('>')[-1]
    author=authorsnip.strip()
    try:
        datesnip=bulktext.split('<meta property="article:published" itemprop="datePublished" content="')[1].split('"')[0]
        datesnipdiv=datesnip.split(' ')
        day=datesnipdiv[1]
        month=translateMonth(datesnipdiv[2])
        year=datesnipdiv[3]
    except:
        datesnip=bulktext.split('<time datetime="')[1].split('"')[0].split('| ')[1]
        datesnipdiv=datesnip.split(' ')
        day=datesnipdiv[0]
        if len(day)<2:
            day='0'+day
        month=translateMonth(datesnipdiv[2])
        year=datesnipdiv[-1]
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end eltiempo

###eluniversal
def eluniversalgenerator(maxnumber=25):
    listofurls=[]
    caturl='http://www.eluniversal.com.mx/opinion-columnas-articulos.html'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<div id="noteContent">')[1]
    relchunk=relchunk.split('<a href="http://foros.eluniversal.com.mx"><h4 class=')[0]
    chops=relchunk.split('<a class="linkBlack"') ##columns and editorials
    chops+=relchunk.split('<h2 class="linkBlueBigTimes"') #featured
    #chops+=relchunk.split('<h3 class="linkBlueMedium"><a') #excluding blogs for now
    urlinicius=''
    for chop in chops[1:]:
        try:
            urlterminus=chop.split(' href="')[1].split('"')[0]
            fullurl=urlinicius+urlterminus
            listofurls.append(fullurl)
        except:
            print('Fail')
    for url in listofurls:
        if url.startswith('/'):
            listofurls.remove(url)
    for url in listofurls[:maxnumber]:
        parsethis=eluniversalreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def eluniversalreader(url):
    source='El Universal (MX)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    if '<h3>¿No es suscriptor de EL UNIVERSAL?</h3>' in bulktext:
        print('Excluding premium article')
        return ('', '0', '', '', '', '')
    actualtext=bulktext.split('<div class="noteText">')
    actualtext=actualtext[1].split('<div id="paginatorFooter">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<h2 class="noteTitle">')[1].split('</h2>')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<div id="noteContent"><span class="noteColumnist">')[1].split('</span>')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split("<META name='date' content='")[1].split("'")[0]
    datesnip=datesnip.replace('-', '')
    date=datesnip.strip()
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end eluniversal

###eluniverso
def eluniversogenerator():
    listofurls=[]
    caturl='http://www.elmundo.es/opinion.html'
    catpage=fetchURL(caturl).read().decode('iso-8859-15') #rebels
    relchunk=catpage.split('<div class="cabecera-seccion">')[1]
    relchunk=relchunk.split('<section class="hot-topics">')[0]
    listofurls+=re.findall(r'(http://www.elmundo.es/opinion/\d{4}/.*)"', relchunk)
    listofurls=set(listofurls)
    for url in listofurls:
        parsethis=eluniversoreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def eluniversoreader(url):
    source='El Universo (ES)'
    bulktext=fetchURL(url).read().decode('iso-8859-15', errors='replace')
    actualtext=bulktext.split('itemprop="articleBody"')
    actualtext=actualtext[1].split('<section class="valoracion" id="valoracion">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<h1 itemprop="headline">')[1].split('</h1>')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('s.prop75="')[1].split('";')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split('<meta property="article:published_time" content="')[1].split('T')[0]
    date=datesnip.strip().replace('-', '')
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end eluniverso

###excelsior
def excelsiorgenerator(maxnumber=6):
    listofurls=[]
    caturl='http://www.excelsior.com.mx/opinion'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<div class = "mb2 float-left width664px height50 spriteFull background-hoy-escriben" >  </div>')[1]
    relchunk=relchunk.split('"float-left width664px placa-seccion-opinion color-nacional"')[0]
    chops=relchunk.split('<div class = "option-section-title-text" >')
    urlinicius=''
    for chop in chops[1:]:
        urlterminus=chop.split(' href = "')[1].split('"')[0]
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=excelsiorreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def excelsiorreader(url):
    source='Excélsior (MX)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    actualtext=bulktext.split('<!-- body -->')
    actualtext=actualtext[1].split('<!-- /body -->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<span id="node-autor"')[1].split('</a>')[0].split('>')[-1]
    author=authorsnip.strip()
    datesnip=bulktext.split('<span id="node-date"')[1].split('</span>')[0].split('>')[-1]
    datesnip=datesnip.strip().split(' ')[0]
    datesnipdiv=datesnip.split('/')
    year=datesnipdiv[2]
    month=datesnipdiv[1]
    day=datesnipdiv[0]
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end excelsior


###lanacion
def lanaciongenerator(maxnumber=20):
    listofurls=[]
    caturl='http://www.lanacion.com.ar/opinion'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('itemtype="http://data-vocabulary.org/Breadcrumb">')[1]
    relchunk=relchunk.split('<section id="informacion2">')[0]
    urlregex=r'<a href="(\/\d+-\S*)" class="info">'
    listofurls+=re.findall(urlregex, relchunk)[:maxnumber]
    listofurls=set(listofurls)
    for url in listofurls:
        if not url.startswith('http://'):
            url='http://lanacion.com.ar'+url
        parsethis=lanacionreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def lanacionreader(url):
    source='La Nación (AR)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    actualtext=bulktext.split('<section id="cuerpo"')
    actualtext=actualtext[1].split('<span class="fin">')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('LN.NotaTM.authors="')[1].split('";')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split('<span class="fecha" itemprop="datePublished" content="')[1].split('"')[0]
    datesnipdiv=datesnip.strip().split(' ')
    year=datesnipdiv[-1]
    day=datesnipdiv[1]
    if len(day)<2:
        day='0'+day
    month=translateMonth(datesnipdiv[3])
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end lanacion


###milenio
def mileniogenerator(maxnumber=100):
    listofurls=[]
    caturl='http://www.milenio.com/firmas/'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<h3 class="index-title">')[1]
    chops=relchunk.split('<h3 class="entry-short">')
    urlinicius='http://www.milenio.com/'
    for chop in chops[1:]:
        urlterminus=chop.split('<a class="lnk" href="')[1].split('"')[0]
        fullurl=urlinicius+urlterminus
        listofurls.append(fullurl)
    for url in listofurls[:maxnumber]:
        parsethis=milenioreader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def milenioreader(url):
    source='Milenio (MX)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    actualtext=bulktext.split('<div itemprop="articleBody"')
    actualtext=actualtext[1].split('<!-- END: NESTED GRID 1/4 - 3/4 -->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<meta name="Author" content="')[1].split('"')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split('<meta name="Pubdate" content="')[1].split('"')[0]
    date=datesnip.strip().replace('-', '')
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end milenio

###prensalibre
def prensalibregenerator():
    listofurls=[]
    caturl='http://www.prensalibre.com/opinion/'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<!-- LEFT COL -->')[1]
    relchunk=relchunk.split('<!-- RIGHT COL -->')[0]
    urlregex=r'<h2><a href="(\/opinion\/\S+)">.+</a></h2>'
    listofurls+=re.findall(urlregex, relchunk)
    listofurls=set(listofurls)
    for url in listofurls:
        if not url.startswith('http://'):
            url='http://prensalibre.com'+url
        parsethis=prensalibrereader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def prensalibrereader(url):
    source='Prensa Libre (GT)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    actualtext=bulktext.split('<!-- Texto de Opinión -->')
    actualtext=actualtext[1].split('<!-- Otras noticias de la sección -->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta name="og:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<p class="author"><strong>')[1].split('</strong> </p>')[0]
    author=authorsnip.strip()
    dateregex=r'(\d{2}\/\d{2}\/\d{2}) - \d{2}:\d{2}'
    datesnip=re.findall(dateregex, bulktext)[0]
    datesnipdiv=datesnip.split('/')
    day=datesnipdiv[0]
    month=datesnipdiv[1]
    year='20'+datesnipdiv[2] #This will work until year 2100
    date=year+month+day
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end prensalibre

###semana
def semanagenerator():
    listofurls=[]
    caturl='http://www.semana.com/seccion/opinion-online/81-1'
    catpage=fetchURL(caturl).read().decode('utf8')
    relchunk=catpage.split('<div id="espacioColumnistas" >')[1]
    relchunk=relchunk.split('<!--hasta aca se carga la sección-->')[0]
    urlregex=r'<a href="(http:\/\/www\.semana\.com\/opinion\/articulo\/\S+)"'
    listofurls+=re.findall(urlregex, relchunk)
    listofurls=set(listofurls)
    for url in listofurls:
        parsethis=semanareader(url)
        hits=int(parsethis[1])
        if hits>threshold:
            logRow(parsethis)
def semanareader(url):
    source='Semana (CO)'
    bulktext=fetchURL(url).read().decode('utf8', errors='replace')
    actualtext=bulktext.split('<div class="container_article" id="contents" >')
    actualtext=actualtext[1].split('<!-- Recs&ads widget start -->')[0]
    hitsinfo=hitcounter(actualtext)
    hits=hitsinfo[0]
    desc=hitsinfo[1]
    titlesnip=bulktext.split('<meta property="ps:title" content="')[1].split('"')[0]
    title=titlesnip.strip()
    linkedtitle='<a href="'+url+'">'+title+'</a>'
    authorsnip=bulktext.split('<meta property="ps:author" content="')[1].split('"')[0]
    author=authorsnip.strip()
    datesnip=bulktext.split('<meta name="cXenseParse:recs:articlepublicationdate" content="')[1].split('"')[0]
    datesnip=datesnip.split(' ')[0]
    datesnipdiv=datesnip.split('/')
    date=datesnipdiv[-1]+datesnipdiv[-2]+datesnipdiv[-3]
    for i in (source, title, author, date):
        print(i)
    return (linkedtitle, str(hits), source, date, author, desc)
###end semana

###EXECUTION COMMANDS
startLog()

claringenerator()
elcomercioPEgenerator()
elespectadorgenerator()
elmercuriogenerator()
elnacionalgenerator()
elpaisgenerator()
eltiempogenerator()
eluniversalgenerator()
eluniversogenerator()
excelsiorgenerator()
lanaciongenerator()
mileniogenerator()
prensalibregenerator()
semanagenerator()


endLog()
        
