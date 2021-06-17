from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Product
from .serializers import ProductSerializer


class TalpaResolveAvailability(APIView):
    def get(self, request, format=None):
        return Response({"result": True})


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
