import json
import base64

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from jsonschema import validate
from jsonschema import ValidationError
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login

from .models import Item, Review

GOOD_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'title': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 64
        },
        'description': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 1024
        },
        'price': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 1000000
        },
    },
    'required': ['title', 'description', 'price'],
}

REVIEW_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'text': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 1024
        },
        'grade': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 10
        },
    },
    'required': ['text', 'grade'],
}


@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):
    """View для создания товара."""

    def post(self, request):
        coded_data = request.headers['authorization'].split()[1]
        decoded_data = base64.b64decode(coded_data).decode('utf-8')
        username, password = decoded_data.split(':')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_staff:
                return JsonResponse({}, status=201)
            return JsonResponse({}, status=403)
        return JsonResponse({}, status=401)
        # try:
        #     data = json.loads(request.body)
        #     validate(data, GOOD_SCHEMA)
        #     good = Item(**data)
        #     good.save()
        #     item_id = good.id
        #     return JsonResponse({'id': item_id}, status=201)
        # except json.JSONDecodeError:
        #     return JsonResponse({'errors': 'Запрос не прошел валидацию'}, status=400)
        # except ValidationError:
        #     return JsonResponse({'errors': 'Запрос не прошел валидацию'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):
    """View для создания отзыва о товаре."""

    def post(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({'errors': 'Товара с таким id не существует'}, status=404)
        try:
            data = json.loads(request.body)
            validate(data, REVIEW_SCHEMA)
            data['item'] = item
            review = Review(**data)
            review.save()
            review_id = review.id
            return JsonResponse({'id': review_id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Запрос не прошел валидацию'}, status=400)
        except ValidationError:
            return JsonResponse({'errors': 'Запрос не прошел валидацию'}, status=400)


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):
        try:
            item = Item.objects.prefetch_related('review_set').get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse(status=404, data={})
        data = model_to_dict(item)
        item_reviews = [model_to_dict(n) for n in item.review_set.all()]
        item_reviews = sorted(item_reviews, key=lambda review: review['id'], reverse=True)[:5]
        for review in item_reviews:
            review.pop('item', None)
        data['reviews'] = item_reviews
        return JsonResponse(data, status=200)
