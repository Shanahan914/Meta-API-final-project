from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from .models import *
import bleach

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(
        validators=[UniqueValidator(
            queryset=MenuItem.objects.all())]
            )

    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'inventory', 'category_id', 'category']

    def validate(self, attrs):
        if 'title' in attrs:
            attrs['title'] = bleach.clean(attrs['title'])
        if 'price' in attrs:
            if(attrs['price'] < 2.00):
                raise serializers.ValidationError('price should not be less than 2.00')
        if 'inventory' in attrs:
            if(attrs['inventory']< 0):
                raise serializers.ValidationError('inventory cannot be negative')
        return super().validate(attrs)
    
class MenuItemDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price']
    

class CartItemsSerializer(serializers.ModelSerializer):
    item = MenuItemsSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['item', 'quantity', 'browser']
        read_only_fields = ['browser']
        

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only = True)
    customer_id = serializers.IntegerField(write_only=True)
    driver = UserSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'customer', 'total_price', 'status', 'date', 'driver_id', 'driver']
    

class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemDescriptionSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['item' ,'quantity' ]
        depth = 1
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=CartItem.objects.all(),
        #         fields = ['order', 'item']
        #     )
        # ]

class OrderSerializer2(serializers.ModelSerializer):
    customer = UserSerializer(read_only = True)
    driver = UserSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True)
    items_for_order = OrderItemSerializer(read_only=True, many=True)
    class Meta:
        model = Order
        depth=1
        fields = ['id', 'customer', 'total_price', 'status', 'date', 'driver_id', 'driver', 'items_for_order']
        read_only_fields = ['id', 'customer', 'total_price', 'date', 'driver', 'items_for_order']

    def validate(self, attrs):
        request = self.context.get('request')
        method = request.method if request else None
        if method == 'PATCH':
            if 'driver_id' not in attrs and 'status' not in attrs:
                raise serializers.ValidationError('You must provide at least one of status or driver_id')
        elif method == 'PUT':
            if 'driver_id' not in attrs:
                raise serializers.ValidationError({'driver_id': 'This field is required for PUT requests.'})
            if 'status' not in attrs:
                raise serializers.ValidationError({'status': 'This field is required for PUT requests.'})
        return super().validate(attrs)