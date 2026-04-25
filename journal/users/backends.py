from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"EmailBackend вызван: username={username}")
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            print(f"Найден: {user}")
        except User.DoesNotExist:
            print("Не найден")
            return None

        check = user.check_password(password)
        can_auth = self.user_can_authenticate(user)
        print(f"check_password: {check}, can_authenticate: {can_auth}")

        if check and can_auth:
            print("Возвращаю пользователя")
            return user

        return None