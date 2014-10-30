from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from nagios_registration.models import Host, HostGroup, Service
from nagios_registration.auth import authenticate_application
import json
from oauth_provider.decorators import oauth_required


###
#
# api methods
#
###
@csrf_exempt
@authenticate_application
def host(request):
    def _get(request):
        hosts = Host.objects.filter(is_active=True)
        host_list = []
        for host in hosts:
            host_list.append(host.json_data())

        return HttpResponse(json.dumps(host_list),
                            content_type="application/json")

    def _post(request):
        try:
            json_data = json.loads(request.body)

            new_host = Host.objects.create(name=json_data["name"],
                                           address=json_data["address"],
                                           )

            return HttpResponse(json.dumps(new_host.json_data()))

        except Exception as ex:
            response = HttpResponse(ex)
            response.status_code = 500
            return response

    if request.method == "GET":
        return _get(request)

    if request.method == "POST":
        return _post(request)


@csrf_exempt
@authenticate_application
def host_group(request):
    def _get(request):
        hostgroups = HostGroup.objects.all()
        hostgroup_list = []
        for group in hostgroups:
            hostgroup_list.append(group.json_data())

        return HttpResponse(json.dumps(hostgroup_list),
                            content_type="application/json")

    def _post(request):
        try:
            json_data = json.loads(request.body)

            new_group = HostGroup.objects.create(name=json_data["name"],
                                                 alias=json_data["alias"],
                                                 )

            return HttpResponse(json.dumps(new_group.json_data()))

        except Exception as ex:
            print "Err: ", ex
            response = HttpResponse(ex)
            response.status_code = 500
            return response

    def _patch(request):
        try:
            json_data = json.loads(request.body)
            hostname = json_data["host"]
            groupname = json_data["group"]

            group = HostGroup.objects.get(name=groupname)
            host = Host.objects.get(name=hostname)

            group.hosts.add(host)

            return HttpResponse("")

        except Exception as ex:
            print "Err: ", ex
            response = HttpResponse(ex)
            response.status_code = 500
            return response

    if request.method == "GET":
        return _get(request)

    if request.method == "POST":
        return _post(request)

    if request.method == "PATCH":
        return _patch(request)


@csrf_exempt
@authenticate_application
def service(request):
    def _get(request):
        services = Services.objects.all()
        services_list = []
        for service in services:
            services_list.append(service.json_data())

        return HttpResponse(json.dumps(services_list),
                            content_type="application/json")

    def _post(request):
        try:
            json_data = json.loads(request.body)

            bs = json_data["base_service"]
            desc = json_data["description"]
            cc = json_data["check_command"]

            cg = None
            if "contact_groups" in json_data:
                cg = json_data["contact_groups"]

            new_service = Service.objects.create(base_service=bs,
                                                 description=desc,
                                                 contact_groups=cg,
                                                 check_command=cc,
                                                 )

            return HttpResponse(json.dumps(new_service.json_data()))

        except Exception as ex:
            print "Err: ", ex
            response = HttpResponse(ex)
            response.status_code = 500
            return response

    def _patch(request):
        try:
            json_data = json.loads(request.body)
            hostname = json_data["host"]
            servicename = json_data["service"]

            service = Service.objects.get(description=servicename)
            host = Host.objects.get(name=hostname)

            service.hosts.add(host)

            return HttpResponse("")

        except Exception as ex:
            print "Err: ", ex
            response = HttpResponse(ex)
            response.status_code = 500
            return response

    if request.method == "GET":
        return _get(request)

    if request.method == "POST":
        return _post(request)

    if request.method == "PATCH":
        return _patch(request)


###
#
# Methods supporting the web ui
#
###
def redirect_to_home(request):
    return HttpResponseRedirect(reverse("nagios_registration_home"))


@login_required
def home(request):
    return render_to_response("home.html", {
        "base_url": reverse("nagios_registration_home"),
    }, RequestContext(request))


@login_required
def ui_data(request):
    hosts = Host.objects.filter(is_active=True)

    host_list = []
    for host in hosts:
        host_list.append(host.json_data())

    return HttpResponse(json.dumps(host_list), content_type="application/json")
