from django.shortcuts import render
from .forms import ContactGeneral, BerneseTools
from .mail import enviar_email
from django.http import HttpResponse
from datetime import datetime
import threading
from bernese.core.rinex import date2gpsWeek
from urllib.request import urlopen

def index(request):
	# return HttpResponse('Em manutenção!')
	template_name = 'index.html'
	context = {}
	context['isHome'] = True
	return render(request, template_name, context)

def tools(request):
	template_name = 'tools.html'
	context = {}
	context['fileList'] = []

	if request.method == 'POST':

		form = BerneseTools(request.POST)

		if form.is_valid():

			rnxDate = datetime.strptime(str(form.cleaned_data['date']),'%Y-%m-%d')

			weekDay = date2gpsWeek(rnxDate)

			if rnxDate.year > 1999:
				anoRed = rnxDate.year - 2000
			else:
				anoRed = rnxDate.year - 1900

			sClkFile = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/COD{}.CLK.Z'.format(rnxDate.year,weekDay)
			sEphFile = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/COD{}.EPH.Z'.format(rnxDate.year,weekDay)
			sIonFile = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/COD{}.ION.Z'.format(rnxDate.year,weekDay)
			sErpFile = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/COD{}.ERP.Z'.format(rnxDate.year,weekDay)
			sP1C1File = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/P1C1{:02d}{:02d}.DCB.Z'.format(rnxDate.year,anoRed,rnxDate.month)
			sP1P2File = 'http://www.aiub.unibe.ch/download/CODE/{:04d}/P1P2{:02d}{:02d}.DCB.Z'.format(rnxDate.year,anoRed,rnxDate.month)

			sfileList = [sClkFile, sEphFile, sIonFile, sErpFile, sP1C1File, sP1P2File]

			# Verifica se o arquivo existe, se não existir remove da lista
			for sfile in sfileList:
				try:
					testLink = urlopen(sfile)
				except:
					i = sfileList.index(sfile)
					sfileList[i] = ''

			context['fileList'] = sfileList

	else:
		form = BerneseTools()

	context['form'] = form
	context['isTools'] = True
	return render(request, template_name, context)

# def ephem(request,date):
# 	template_name = 'ephem.html'
# 	context = {}
#
# 	date = datetime.strptime(date,'%Y-%m-%d')
#
#
#
# 	context['isTools'] = True
# 	return render(request, template_name, context)


def about(request):
	template_name = 'about.html'
	context = {}
	context['isAbout'] = True
	return render(request, template_name, context)

def contact(request):
	template_name = 'contact.html'
	context = {}
	if request.method == 'POST':
		form = ContactGeneral(request.POST)
		if form.is_valid():
			context['is_valid'] = True
			email_context = {
				'name' : form.cleaned_data['name'],
				'email' : form.cleaned_data['email'],
				'message' : form.cleaned_data['message'],
			}
			enviar_email(**email_context)
			form = ContactGeneral()
	else:
		form = ContactGeneral()

	context['form'] = form
	context['isContact'] = True
	return render(request, template_name, context)

def monitor(request):
	msg = 'Processamentos ativos: '
	nproc = 0
	for tr in threading.enumerate():
		if tr.name[:4] == 'bern':
			msg += tr.name + ', '
			nproc += 1

	if not nproc: msg += 'Nenhum'

	return HttpResponse(msg)

def custom_error_500_view(request):
	template_name = '500.html'
	context = {}
	return render(request, template_name, context)
