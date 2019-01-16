import json
import base64
import os
import csv

from django.shortcuts import redirect, render_to_response
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.renderers import TemplateHTMLRenderer

from .serializers import TokenSerializer, UserSerializer, LoginSerializer
from .models import Employee, Organisation
from .tasks import file_download_task


# Get the JWT settings.
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
User = get_user_model()


ERROR_405 = "405 Method Not Allowed"

class RegisterView(APIView):
    """
    POST api/register/
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        serializer = UserSerializer()
        return Response({'serializer': serializer})

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                data = {
                    'id': user.user_id,
                    'token': jwt_encode_handler(jwt_payload_handler(user)),
                    'email': serializer.data.get('email', ''),
                    'success': True
                }
                if request.accepted_renderer.format == "html":
                    return redirect("login")
                return Response(data, status=status.HTTP_201_CREATED)
            return HttpResponse("User not registered successfully")
        return HttpResponse(str(serializer.user_check.message))
        

class LoginView(APIView):
    """
    POST api/login/
    """
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        serializer = LoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            data = {
                    'id': user.user_id,
                    'token': jwt_encode_handler(jwt_payload_handler(user)),
                    'email': email,
                    'success': True
                }
            serializer = TokenSerializer(data=data)
            serializer.is_valid()
            if request.accepted_renderer.format == "html":
                return redirect("add_snippet")
            else:
                return Response(data, status=status.HTTP_200_OK)
        serializer = LoginSerializer()
        return Response({"serializer": serializer})


class EmployeeData(APIView):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        resp_dict = {"success": True, "data": {},
                     "summary": "Details found successfully"}
        try:
            user = request.user
            address = request.GET.get('address', None)
            if address:
                query = Employee.objects.filter(address=address)
                data = []
                for i in query:
                    d = dict()
                    d["employee_name"] = i.employee_name
                    d["address"] = i.address
                    data.append(d)
                return Response(data, status=status.HTTP_200_OK) 
        except Exception as e:
            return HttpResponse(str(e))
        return JsonResponse(resp_dict)

class OrganisationData(APIView):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        resp_dict = {"success": True, "data": {},
                     "summary": "Details found successfully"}
        try:
            user = request.user
            address = request.GET.get('address', None)
            if address:
                query = Organisation.objects.filter(org_address=address)
                data = []
                for i in query:
                    d = dict()
                    d["org_name"] = i.org_name
                    d["org_address"] = i.org_address
                    d["org_owner"] = i.org_owner
                    d["org_type"] = i.org_type
                    data.append(d)
                return Response(data, status=status.HTTP_200_OK) 
        except Exception as e:
            return HttpResponse(str(e))
        return JsonResponse(resp_dict)

class DownloadFile(APIView):
    # authentication_classes = (SessionAuthentication, )
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        resp_dict = {"success": True, "data": {},
                     "summary": "Files will be downloaded shortly"}
        try:
            user = request.user
            data = request.data.get('data', None)
            if len(data) >= 1:
                file_download_task.delay(data, 1, request.META['HTTP_HOST'])
                return JsonResponse(resp_dict)
        except Exception as e:
            resp_dict["success"] = False
            resp_dict["summary"] = str(e)
        return JsonResponse(resp_dict)

def check(request):
    return render(request,"test.html")
