from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from api.utils import decode_id

from .models import Recipe


class RecipeShortLinkRedirectView(View):

    def get(self, request, code):
        try:
            recipe_id = decode_id(code)
        except ValueError:
            raise Http404('Некорректная короткая ссылка.')
        get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/recipes/{recipe_id}/')
