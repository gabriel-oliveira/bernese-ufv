from django.template.loader import render_to_string
from django.template.defaultfilters import striptags
from django.core.mail import EmailMultiAlternatives, send_mail
from bernese.settings import DEFAULT_FROM_EMAIL, CONTACT_EMAIL, BASE_DIR, DEBUG
from datetime import datetime
from threading import Thread
from bernese.core.log import log
import sys


def send_mail_template(subject, template_name, context, recipient_list, pathFile,
	from_email=DEFAULT_FROM_EMAIL, fail_silently=False, pathFileName=None):

	message_html = render_to_string(template_name, context)

	message_txt = striptags(message_html)

	email = EmailMultiAlternatives(subject=subject, body=message_txt, from_email=from_email, to=recipient_list)
	email.attach_alternative(message_html, "text/html")

	if pathFile and not DEBUG:
		with open(pathFile,'rb') as rfile:
			if not pathFileName: pathFileName = rfile.name
			afile = rfile.read()
			email.attach(pathFileName,afile)

	try:

		email.send(fail_silently=fail_silently)

		return True

	except Exception as e:

		log('Erro no envio do email.')
		erroMsg = sys.exc_info()
		log(str(erroMsg[0]))
		log(str(erroMsg[1]))

		return False

def bkp_msg(msg_txt):

	with open(BASE_DIR + '/backupMsgContato.txt','a',encoding='utf-8', errors='surrogateescape') as f:
		f.write(msg_txt.encode().decode('utf-8','ignore'))


def enviar_email(name,email,message,mpathFile=''):
	subject = 'Contato'
	context = {
		'name': name,
		'email': email,
		'message': message,
	}
	template_name = 'contact_email.html'


	# Salvando backup da mensagem no servidor
	msg_txt = 'Em: ' + datetime.now().isoformat(' ','seconds') + '\n'
	msg_txt += 'Nome: {name}\nE-mail: {email}\nMessage: {message}\n'.format(**context)
	if mpathFile: msg_txt += mpathFile + '\n'

	bkp_msg(msg_txt)

	# Enviando o email em um processamento paralelo
	Thread(target=send_mail_template,
		args = (subject, template_name, context, [CONTACT_EMAIL],mpathFile)
		).start()


def send_result_email(to_email,message,mpathFile='',mpathFileName=None):
	subject = '[GNSS-UFV] Resultado do Processamento'

	context = {
		'message': message,
	}
	template_name = 'result_email.html'

	# Salvando backup da mensagem no servidor
	msg_txt = 'Em: ' + datetime.now().isoformat(' ','seconds') + '\n'
	msg_txt += 'Resultado do processamento:\n'
	msg_txt += to_email + '\n'
	msg_txt += message + '\n'
	if mpathFile: msg_txt += mpathFile + '\n'

	# Enviando o email
	if not send_mail_template(subject, template_name, context, [to_email], mpathFile, pathFileName=mpathFileName):
		msg_txt += 'EMAIL NÃO ENVIADO!!!\n'

	bkp_msg(msg_txt)
