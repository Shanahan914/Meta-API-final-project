from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound 
from rest_framework.decorators import action, APIView, api_view, permission_classes
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import get_object_or_404


# Create your views here.

# /menu-items ;  get, post  ; filter by price and category
class menu_items(generics.ListCreateAPIView):
    serializer_class = MenuItemsSerializer
    ordering_fields = ['price']
    search_fields=['title','category__name']

    def get_queryset(self):
        queryset = MenuItem.objects.select_related('category').all()
        category = self.request.query_params.get('category')
        max_price = self.request.query_params.get('max_price')
        min_price = self.request.query_params.get('min_price')
        if category:
            queryset = queryset.filter(category__name = category)
        if max_price:
            queryset = queryset.filter(price__lte = max_price)
        if min_price:
            queryset = queryset.filter(price__gte = min_price)
        return queryset
    
    def get_permissions(self):
        permission_classes=[]
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            permission_classes =[IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]
  

# /menu-items/{menuItem} ; get, put, patch, delete

class single_menu_item(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemsSerializer

    def get_permissions(self):
        permission_classes=[]
        if self.request.method !='GET':
            permission_classes =[IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]


# cart/menu-items ; get, post, delete
class cart(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartItemsSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsCustomer]

    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.filter(browser = user)
        print(queryset)
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        item = serializer.validated_data['item']

        if CartItem.objects.filter(browser=user, item=item).exists():
            raise ValidationError("This item is already in your cart.")
        
        serializer.save(browser = self.request.user)

    @action(detail=False, methods=['delete'])
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        queryset = CartItem.objects.filter(browser = user)
        queryset.delete()
        return Response({"message":"deleted"}, status.HTTP_200_OK)
    

# /orders ; get, post
class orders(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['price', 'date', 'status']
    search_fields=['customer__username','driver__username']

    def get_queryset(self):
        queryset = Order.objects.select_related('customer', 'driver').all()
        if self.request.user.groups.filter(name='customer').exists():
            queryset = queryset.filter(customer = self.request.user)
        if self.request.user.groups.filter(name='driver').exists():
            print('driver')
            queryset = queryset.filter(driver = self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status = status)
        return queryset
    
    def create(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='customer').exists():
            user = self.request.user
            queryset = CartItem.objects.filter(browser = user)
            if len(queryset) < 1:
                return Response(status.HTTP_400_BAD_REQUEST)
            item_list = list(queryset.values())
            sum = 0
            for i in range(len(item_list)):
                item_id = item_list[i]['item_id']
                unit_cost = MenuItem.objects.values('price').filter(id = item_id)
                sub_total = float(unit_cost[0]['price']) * int(item_list[i]['quantity'])
                sum += sub_total
            # create order 
            order = Order.objects.create(customer = user, total_price = sum)
            # add order details
            for i in range(len(item_list)):
                item_id = item_list[i]['item_id']
                quant = item_list[i]['quantity']
                item_id_orders = get_object_or_404(MenuItem, id = item_id)
                OrderItem.objects.create(order = order, quantity = quant, item = item_id_orders)
            queryset.delete()
            return Response({"message":"order created"}, status.HTTP_201_CREATED)
        return Response({"message":"you do not have permission"}, status.HTTP_401_UNAUTHORIZED)


#/orders/{orderId} ; get, put, patch, delete, 
class single_order(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer2
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            # If user is in OrderManagers group, allow access to all OrderItems
            return Order.objects.all()
        elif user.groups.filter(name='manager').exists():
            return Order.objects.filter(driver=user)
        else:
            # Otherwise, filter based on the user
            return Order.objects.filter(customer=user)
        
    def get_permissions(self):
        permission_classes=[]
        if self.request.method in ['DELETE', 'PUT']:
            permission_classes =[IsAuthenticated, IsManager]
        if self.request.method in ['PATCH']:
            permission_classes = [IsAuthenticated, IsDriver | IsManager]
        return [permission() for permission in permission_classes]
    
    
    def patch(self, reqyuest, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        serialized_item = OrderSerializer2(data=self.request.data, partial=True)
        serialized_item.is_valid(raise_exception=True)
        if user.groups.filter(name='driver').exists():
            statusD = self.request.data['status']
            if statusD or statusD == 0:
                order.status = statusD
                order.save(update_fields=['status'])
                return Response({"message":"ok"}, status.HTTP_200_OK)
            return Response({"message":"you can only change status"}, status.HTTP_400_BAD_REQUEST)
        if user.groups.filter(name='manager').exists():      
            statusM = self.request.data.get('status')
            driverId = self.request.data.get('driver_id')
            update_fields = []
            if statusM or statusM == 0:
                order.status = statusM
                update_fields.append('status')
            if driverId:
                driver = get_object_or_404(User, id = driverId)
                update_fields.append('driver')
                order.driver = driver
            order.save(update_fields=update_fields)
            return Response({"message":"ok"}, status.HTTP_200_OK)
            

    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def managers(request):
    if request.user.groups.filter(name='manager').exists():
        if request.method == 'GET':
            try:
                group = Group.objects.get(name='manager')
            except Group.DoesNotExist:
                raise NotFound(detail="group not found")
            users = User.objects.filter(groups=group)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name="manager")
                if request.method == 'POST':
                    managers.user_set.add(user)
                # elif request.method == 'DELETE':
                #     managers.user_set.remove(user)
                return Response({"message":"ok"}, status.HTTP_201_CREATED)
    else:
        return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_manager(request, pk):
    if request.user.groups.filter(name='manager').exists():
        user = get_object_or_404(User, id = pk)
        managers = Group.objects.get(name="manager")
        managers.user_set.remove(user)
        return Response({"message":"ok"}, status.HTTP_200_OK)
    else:
         return Response({"message":"you do not have permission"}, status.HTTP_401_UNAUTHORIZED)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def drivers(request):
    if request.user.groups.filter(name='manager').exists():
        if request.method == 'GET':
            try:
                group = Group.objects.get(name='driver')
            except Group.DoesNotExist:
                raise NotFound(detail="group not found")
            users = User.objects.filter(groups=group)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                drivers = Group.objects.get(name="driver")
                if request.method == 'POST':
                    drivers.user_set.add(user)
                return Response({"message":"ok"}, status.HTTP_201_CREATED)
    return Response({"message":"error"}, status.HTTP_401_UNAUTHORIZED)


@api_view(['DELETE'])
def delete_driver(request, pk):
     print(request.user.groups)
     if request.user.groups.filter(name='manager').exists():
        user = get_object_or_404(User, id = pk)
        drivers = Group.objects.get(name="driver")
        drivers.user_set.remove(user)
        return Response({"message":"ok"}, status.HTTP_200_OK)
     else:
         return Response({"message":"you do not have permission"}, status.HTTP_401_UNAUTHORIZED)