from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from addresses.models import Addresses
from addresses.serializers import AddressAddSerializer, AddressListSerializer


# Create your views here.
from users.models import User


class AddressViewSet(ModelViewSet):
    queryset = Addresses.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id= request.query_params.get('id'))
        except:
            return Response(status=401)
        addresses = user.addresses
        try:
            default_address_id = user.default_address.id
        except:
            default_address_id = None
        return Response({'addresses':AddressListSerializer(addresses,many=True).data,'limit':20,'default_address_id':default_address_id})


    def get_serializer_class(self):
        if self.action in('create','update') :
            return AddressAddSerializer
        else:
            return AddressListSerializer
