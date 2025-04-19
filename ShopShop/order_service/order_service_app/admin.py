from django.contrib import admin
from .models import Order, OrderStatusHistory

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    readonly_fields = ('old_status', 'new_status', 'timestamp')
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'order_status', 'created_at', 'updated_at')
    inlines = [OrderStatusHistoryInline]

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'old_status', 'new_status', 'timestamp')
    list_filter = ('order', 'new_status')
    readonly_fields = ('order', 'old_status', 'new_status', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False