from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum
from datetime import datetime
from django.urls import reverse
from .models import DeliveryPerson, BonusSettings
from django.contrib import admin
from django.db.models import Sum, Count
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum
from datetime import datetime
from .models import Order
from django.contrib import admin
from django.db.models import Sum
from django import forms
from django.contrib import messages
from .models import Order
from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import (
    User, Client, Employee, DeliveryPerson,
    Category, Restaurant, Product, Order, OrderItem, Delivery
)


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="От дата",
        widget=forms.DateInput(attrs={'type': 'date', 'required': True})
    )
    end_date = forms.DateField(
        label="До дата",
        widget=forms.DateInput(attrs={'type': 'date', 'required': True})
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total_price', 'status', 'created_at')
    actions = ['calculate_revenue_action']
    def calculate_revenue_action(self, request, queryset):
        url = reverse('admin:revenue_report')
        ids = ','.join(str(pk) for pk in queryset.values_list('id', flat=True))
        return redirect(f"{url}?ids={ids}")
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('revenue-report/', self.admin_site.admin_view(self.revenue_report), name='revenue_report'),
        ]
        return custom_urls + urls

    def revenue_report(self, request):
        form = DateRangeForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            total = Order.objects.filter(
                created_at__date__range=[start_date, end_date],
                status='delivered'
            ).aggregate(total=Sum('total_price'))['total'] or 0

            messages.success(
                request,
                f"✅ Оборот от {start_date} до {end_date}: {total:.2f} лв."
            )
            return redirect('admin:accounts_order_changelist')

        context = {
            'form': form,
            'title': 'Изчисли оборот',
            'opts': self.model._meta,
        }
        return render(request, 'admin/revenue_report.html', context)


def supplier_income_report(self, request):
    form = DateRangeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # Филтриране на доставените поръчки за периода
        delivered_orders = Order.objects.filter(
            status='delivered',
            created_at__date__range=[start_date, end_date]
        )

        # Групиране по доставчик и изчисляване на приходите
        supplier_income = delivered_orders.values('delivery_person__user__username').annotate(
            total_income=Sum('total_price')
        )

        context = {
            'title': 'Справка за приходи по доставчици',
            'opts': self.model._meta,
            'supplier_income': supplier_income,
            'start_date': start_date,
            'end_date': end_date,
        }
        return TemplateResponse(request, 'admin/supplier_income_report.html', context)

    context = {
        'form': form,
        'title': 'Изчисли приходи по доставчици',
        'opts': self.model._meta,
    }
    return TemplateResponse(request, 'admin/supplier_income_form.html', context)


def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="delivery_earnings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Доставчик', 'Период', 'Приходи', 'Брой поръчки'])

    for item in queryset:
        writer.writerow([
            item.delivery_person,
            f"{item.start_date} до {item.end_date}",
            item.total_earnings,
            item.order_count
        ])
    return response


@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'earnings_report_link', 'total_bonuses', 'total_turnover')
    readonly_fields = ('total_bonuses',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/earnings-report/',
                 self.admin_site.admin_view(self.earnings_report),
                 name='deliveryperson_earnings_report')
        ]
        return custom_urls + urls

    def earnings_report_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Справка за оборот</a>',
            reverse('admin:deliveryperson_earnings_report', args=[obj.pk])
        )

    earnings_report_link.short_description = "Действия"

    def earnings_report(self, request, object_id):
        delivery_person = get_object_or_404(DeliveryPerson, pk=object_id)

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Изчисляване на оборота за периода
            period_orders = Order.objects.filter(
                delivery_person=delivery_person,
                created_at__date__range=[start_date, end_date],
                status='delivered'
            )
            period_turnover = period_orders.aggregate(total=Sum('total_price'))['total'] or 0

            # Общ оборот (от total_turnover полето в DeliveryPerson)
            total_turnover = delivery_person.total_turnover

            context = {
                'delivery_person': delivery_person,
                'start_date': start_date,
                'end_date': end_date,
                'period_turnover': period_turnover,  # Оборот за периода
                'total_turnover': total_turnover,  # Общ оборот (цялата история)
                'order_count': period_orders.count()
            }
            return render(request, 'admin/delivery_earnings_report.html', context)

        return render(request, 'admin/delivery_earnings_form.html', {
            'delivery_person': delivery_person
        })
@admin.register(BonusSettings)
class BonusSettingsAdmin(admin.ModelAdmin):
    list_display = ('min_turnover', 'bonus_amount', 'is_active')
    list_editable = ('is_active',)






# Регистрирайте всички модели
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Delivery)

