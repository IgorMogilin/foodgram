from recipes.models import UserRecipeRelation

ERRORS_MAP = {
    'favorite': {
        'exists': 'Рецепт уже в избранном',
        'not_exists': 'Рецепта нет в избранном',
    },
    'shopping_cart': {
        'exists': 'Рецепт уже в корзине',
        'not_exists': 'Рецепта не было в корзине',
    },
}

RELATION_TYPES = {
    'favorite': UserRecipeRelation.FAVORITE,
    'shopping_cart': UserRecipeRelation.CART,
}


def get_errors_and_relation(type_):
    """
    Возвращает сообщения об ошибках и тип
    отношения для указанного действия.
    """

    if type_ not in RELATION_TYPES:
        raise ValueError('Недопустимый тип действия')
    relation_type = RELATION_TYPES[type_]
    return ERRORS_MAP[type_], relation_type
