from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import DeliveryPerson, BonusSettings, Order
from datetime import timedelta
from django.db.models import Sum, Q

class Command(BaseCommand):
    help = 'Автоматично начисляване на бонуси при преминат оборот'

    def handle(self, *args, **options):
        # Взимаме активните настройки
        bonus_settings = BonusSettings.objects.filter(is_active=True).first()
        if not bonus_settings:
            self.stdout.write("Няма активни бонус настройки")
            return

        # Период - последните 30 дни
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        qualified_dps = DeliveryPerson.objects.annotate(
            turnover=Sum('orders__total_price',
                         filter=Q(orders__created_at__range=[start_date, end_date],
                                  orders__status='delivered')
                         )
        ).filter(turnover__gte=bonus_settings.min_turnover)

        # Сигурни сме, че qualified_dps е дефинирана
        for dp in qualified_dps:
            dp.total_bonuses += bonus_settings.bonus_amount
            dp.save()
            self.stdout.write(
                f"Начислен бонус {bonus_settings.bonus_amount} лв. за {dp.user.username} (Оборот: {dp.total_turnover} лв.)")

        self.stdout.write(
            f"Готово! Начислени бонуси на {qualified_dps.count()} доставчика"
        )

'''
# 1. Намираме доставчиците с оборот над прага
        qualified_dps = DeliveryPerson.objects.annotate(
            turnover=Sum('orders__total_price',
                        filter=Q(orders__created_at__range=[start_date, end_date],
                               orders__status='delivered')
        ).filter(turnover__gte=bonus_settings.min_turnover)

        # 2. Начисляваме бонусите
        for dp in qualified_dps:
            dp.total_bonuses += bonus_settings.bonus_amount
            dp.save()
            self.stdout.write(
                f"Начислен бонус {bonus_settings.bonus_amount} лв. за "
                f"{dp.user.username} (Оборот: {dp.turnover} лв.)"
            )

'''