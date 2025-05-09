from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from users.models import User


class IsAuthorOrReadOnly(IsAuthenticated):
    """Проверка прав доступа: разрешает чтение всем, а изменение только автору.

    Наследуется от IsAuthenticated и добавляет проверку авторства:
    - Разрешает безопасные методы (GET, HEAD, OPTIONS) всем пользователям
    - Разрешает изменяющие методы (POST, PUT, PATCH, DELETE) только автору
    - Гарантирует, что пользователь аутентифицирован
    """

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту.

        Args:
            request: Запрос пользователя
            view: View, обрабатывающий запрос
            obj: Объект, к которому проверяются права

        Returns:
            bool: True если запрос безопасный или пользователь - автор объекта,
                  False в противном случае
        """

        return request.method in SAFE_METHODS or obj.author == request.user

    def has_permission(self, request, view):
        """Проверяет общие права доступа до применения к конкретному объекту.

        Args:
            request: Запрос пользователя
            view: View, обрабатывающий запрос

        Returns:
            bool: True если запрос безопасный или пользователь аутенф-ван,
                  False в противном случае
        """

        return request.method in SAFE_METHODS or isinstance(request.user, User)
