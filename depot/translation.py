from modeltranslation.translator import register, TranslationOptions
from depot.models import Depot, Item


@register(Depot)
class DepotTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Item)
class ItemTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)
