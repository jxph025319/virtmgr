import libvirt
import socket
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from virtmgr.model.models import *

def index(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/user/login')

	def get_hosts_status():
		kvm_host = Host.objects.filter(user=request.user.id)
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
			name_ipddr[host.hostname] = (host.id, host.ipaddr, host.login, host.passwd, status)
	   	return name_ipddr
	
	def del_host(host):
		hosts = Host.objects.get(user=request.user.id, hostname=host)
		hosts.delete()

	def add_host(host, ip, usr, passw):
		hosts = Host(user_id=request.user.id, hostname=host, ipaddr=ip, login=usr, passwd=passw)
		hosts.save()

	def get_host_status(hosts):
		for host, info in hosts.items():
			print host, info

	host_info = get_hosts_status()

	if request.method == 'POST':
		action = request.POST.get('action','')
		if action == 'delete':
			host = request.POST.get('host','')
			del_host(host)
			return HttpResponseRedirect('/dashboard/')
		if action == 'add':
			form = AddNewHost(request.POST)
			if form.is_valid():
				field = form.cleaned_data
				name = field['host']
				ipaddr = field['ipaddr']
				login = field['sshusr']
				passw = field['passw']

				hostname = Host.objects.filter(user=request.user, hostname=name)
				ipaddr = Host.objects.filter(user=request.user, ipaddr=ipaddr)

				if not name or not ipaddr or not login or not passw:
					error = 'Inser all fields'
				elif ipaddr or hostname:
					error = 'Inser all fields'
				else:
					add_host(name, ipaddr, login, passw)

				return HttpResponseRedirect('/dashboard/')

	return render_to_response('dashboard.html', locals())
