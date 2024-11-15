import pytz
from app.db.models import ReferralCode, User, UserReferral
from sqladmin import Admin, ModelView

TIMEZONE = 'Asia/Yekaterinburg'


def setup_admin(app, engine):
    admin = Admin(app, engine, title='Админ Панель')

    class UserAdmin(ModelView, model=User):
        """Отображение пользователей."""
        name = 'Пользователь'
        name_plural = 'Пользователи'

        column_searchable_list = [
            User.email
        ]
        column_list = [
            User.id,
            User.email,
        ]

    class ReferralCodeAdmin(ModelView, model=ReferralCode):
        """Отображение реферальных кодов."""
        name = 'Реферальный код'
        name_plural = 'Реферальные коды'

        def expiration_date_taking_timezone(self, value):
            """Получаем время завершения работы кода с учётом часового пояса."""
            return self.expiration_date.astimezone(pytz.timezone(TIMEZONE)) if value else ''

        column_formatters = {
            'expiration_date': expiration_date_taking_timezone
        }

        column_searchable_list = [
            ReferralCode.code
        ]
        column_list = [
            ReferralCode.id,
            ReferralCode.code,
            ReferralCode.expiration_date,
            ReferralCode.is_archived,
            ReferralCode.user_id,
        ]

    class UserReferralAdmin(ModelView, model=UserReferral):
        """Отображение реферальных связей."""
        name = 'Реферальная связь'
        name_plural = 'Реферальные связи'

        column_list = [
            UserReferral.id,
            UserReferral.referrer,
            UserReferral.referred,
        ]

    admin.add_view(UserAdmin)
    admin.add_view(UserReferralAdmin)
    admin.add_view(ReferralCodeAdmin)
