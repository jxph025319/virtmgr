# -*- coding: utf-8 -*-
import re, socket
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from virtmgr.model.models import *

def index(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/user/login')

	def get_hosts_status():
		kvm_host = Host.objects.filter(user=request.user.id).order_by('-id')
		name_ipddr = {}
		for host in kvm_host:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.settimeout(1)
				s.connect((host.ipaddr, 16509))
				s.close()
				status = 1
			except:
				status = 2
			name_ipddr[host.id] = (host.hostname, 
										 host.ipaddr, 
										 host.login, 
										 host.passwd, 
										 status
										 )
	   	return name_ipddr
	
	def del_host(host):
		hosts = Host.objects.get(user=request.user.id, hostname=host)
		hosts.delete()

	def add_host(host, ip, usr, passw):
		hosts = Host(user_id=request.user.id, 
					 hostname=host, 
					 ipaddr=ip, 
					 login=usr, 
					 passwd=passw,
					 state=0
					 )
		hosts.save()
		kvm_host = Host.objects.get(user=request.user.id, hostname=host)
		msg = _('Add server: ')
		msg = msg + host
		error_msg = Log(host_id=kvm_host.id, 
			            type='user', 
			            message=msg, 
			            user_id=request.user.id
			            )
		error_msg.save()

	def get_host_status(hosts):
		for host, info in hosts.items():
			print host, info

#	if request.session['login_kvm'] or request.session['passwd_kvm']:
#		del request.session['login_kvm']
#		del request.session['passwd_kvm']

	host_info = get_hosts_status()
	errors = []

	if request.method == 'POST':
		if request.POST.get('delete',''):
			host = request.POST.get('host','')
			del_host(host)
			return HttpResponseRedirect('/dashboard/')
		if request.POST.get('add',''):
			name = request.POST.get('name','')
			ipaddr = request.POST.get('ipaddr','')
			login = request.POST.get('sshusr','')
			passw = request.POST.get('passw','')
			simbol = re.search('[^a-zA-Z0-9\_]+', name)
			ipsimbol = re.search('[^a-z0-9\.\-]+', ipaddr)
			domain = re.search('[\.]+', ipaddr)
			privat_ip1 = re.search('^172\.16\.', ipaddr)
			privat_ip2 = re.search('^192\.168\.', ipaddr)
			privat_ip3 = re.search('^10\.', ipaddr)
			privat_ip4 = re.search('^127\.', ipaddr)
			if privat_ip1 or privat_ip2 or privat_ip3 or privat_ip4:
				msg = _('IP address can not be a private address space')
				errors.append(msg)
			if len(name) > 20:
				msg = _('The host name must not exceed 20 characters')
				errors.append(msg)
			if ipsimbol or not domain:
				msg = _('Hostname must contain only numbers, or the domain name separated by "."')
				errors.append(msg)
			if simbol:
				msg = _('The host name must not contain any characters and Russian characters')
				errors.append(msg)
			else:
				have_host = Host.objects.filter(user=request.user, hostname=name)
				have_ip = Host.objects.filter(user=request.user, ipaddr=ipaddr)
				if have_host or have_ip:
					msg = _('This host is already connected')
					errors.append(msg)
			if not name:
				msg = _('No hostname has been entered')
				errors.append(msg)
			if not ipaddr:
				msg = _('No IP address has been entered')
				errors.append(msg)
			#if not login:
			#	msg = _('No KVM login was been entered')
			#	errors.append(msg)
			#if not passw:
			#	msg = _('No KVM password was been entered ')
			#	errors.append(msg)
			if not errors:
				add_host(name, ipaddr, login, passw)
				return HttpResponseRedirect('/dashboard/')
	return render_to_response('dashboard.html', locals())
