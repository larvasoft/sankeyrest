from datetime import date

from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import pagination

import jwt

from restapi import settings
from .models import Emp
from .serializers import HR_Serial, Emp_Serial
from rest_framework import generics, mixins, status


def decode(encoded):
    try:
        decrypt = jwt.decode(encoded, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return dict({
            'username': '',
            'id': 0
        })
    return decrypt


# Create your views here.
class Fire(generics.GenericAPIView, mixins.UpdateModelMixin):
    queryset = Emp.objects.all()
    serializer_class = HR_Serial
    lookup_field = 'id'

    def post(self, request, id):
        querysets = Emp.objects.all()
        entries = decode(request.headers.get('Authorisation'))
        for data in querysets:
            if entries['username'] == data.username and entries['id'] == data.id and entries['role']:
                # request.data['end_date'] = date.today()
                print(request.data)
                return self.update(request, id)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)


class HrView(generics.GenericAPIView, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
             mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Emp.objects.all()
    serializer_class = HR_Serial
    # authentication_classes = [SessionAuthentication]
    lookup_field = 'id'

    def get(self, request, id=None):
        querysets = Emp.objects.all()
        entries = decode(request.headers.get('Authorisation'))
        for data in querysets:
            # if 1 == 1:
            if entries['username'] == data.username and entries['id'] == data.id:
                if id:
                    return self.retrieve(request)
                else:

                    return self.list(request)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, id):
        querysets = Emp.objects.all()
        entries = decode(request.headers.get('Authorisation'))
        for data in querysets:
            if entries['username'] == data.username and entries['id'] == data.id:
                return self.update(request, id)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        querysets = Emp.objects.all()
        counts = querysets.count()
        serializer_class = Emp_Serial
        # request.headers.set('authorization','')
        entries = decode(request.headers.get('Authorisation'))
        for data in querysets:

            if entries['username'] == data.username and entries['id'] == data.id:

                request.data['id'] = counts + 1
                print(request.data)
                return self.create(request)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        querysets = Emp.objects.all()
        entries = decode(request.headers.get('Authorisation'))
        for data in querysets:
            print(data)
            if entries['username'] == data.username and entries['id'] == data.id and entries['role']:
                print(request.data)
                return self.destroy(request, id)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)


class Bulk(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Emp.objects.all()

    def post(self, request):
        querysets = Emp.objects.all()
        counts = querysets.count()
        entries = decode(request.headers.get('Authorisation'))
        print(request.data)
        for data in querysets:
            print(entries['role'])
            if entries['username'] == data.username and entries['id'] == data.id and entries['role']:
                i = 1
                for datas in request.data:
                    datas['id'] = counts + i
                    serializer_class = Emp_Serial(data=datas)
                    if serializer_class.is_valid():
                        serializer_class.save()
                    i = i + 1
                return Response(status=status.HTTP_201_CREATED)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)


class Search(generics.GenericAPIView):
    def get(self, request):
        try:
            data = request.session['Authorization']
            print(data)
        except:
            pass
        if data:
            return request.session['Authorisation']
        else:
            print('False')
            return JsonResponse({
                'message': 'False'
            })

    def post(self, request):
        queryset = Emp.objects.all().filter(is_active=True)
        isAdmin = False
        for data in queryset:
            if request.data['username'] == data.username and request.data['password'] == data.password:
                if data.role == 'Admin':
                    isAdmin = True

                payloads = jwt.encode({
                    'username': data.username,
                    'message': 'Found',
                    'role': isAdmin,
                    'id': data.id
                }, settings.SECRET_KEY, algorithm='HS256')
                payload = [{
                    'username': data.username,
                    'message': 'Found',
                    'role': isAdmin,
                    'id': data.id,
                    'secret': "".join(chr(x) for x in payloads)
                }]

                return JsonResponse(payload, safe=False)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            print(request.session['Authorization'])
            del request.session['Authorization']
        except KeyError:
            pass

        return HttpResponse("You're logged out.")


class Empty(generics.GenericAPIView):
    def get(self, id=None):
        return JsonResponse([{'message': 'connected'}], safe=False)


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'pagesize'


class Sort(generics.ListAPIView):
    serializer_class = HR_Serial
    queryset = Emp.objects.all().filter(is_active=True)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('id', 'name', 'username', 'email', 'created_date', 'role', 'is_active', 'end_date')
    ordering_fields = ('id', 'name', 'username', 'email', 'created_date', 'role', 'is_active', 'end_date')
    search_fields = ('id', 'name', 'username', 'email', 'created_date', 'role', 'is_active', 'end_date')
    pagination_class = ExamplePagination


class Searching(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = HR_Serial
    queryset = Emp.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('id', 'name', 'username', 'email', 'created_date', 'role')
    ordering_fields = ('id', 'name', 'username', 'email', 'created_date', 'role')
    search_fields = ('id', 'name', 'username', 'email', 'created_date', 'role')
    pagination_class = ExamplePagination

    def get(self, request):
        querysets = Emp.objects.all().filter(is_active=True)
        entries = decode(request.headers.get('Authorisation'))
        authentication = request.session.get('sessionid')
        print(authentication)
        for data in querysets:
            if entries['username'] == data.username and entries['id'] == data.id:
                return self.list(request)
            else:
                return JsonResponse([{'message': 'Unauthorised'}], safe=False, status=status.HTTP_401_UNAUTHORIZED)
