from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Item, Category, Brand, Color, WornItem
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging
from datetime import date
from django.utils.dateparse import parse_datetime

# logger = logging.getLogger(__name__)

def calendar_view(request):
    return render(request, 'calendar.html')

def get_calendar_data(request):
    start_date = parse_datetime(request.GET.get('start'))
    end_date = parse_datetime(request.GET.get('end'))

    worn_items = WornItem.objects.filter(date__range=(start_date, end_date)).select_related('item')
    events = []

    for worn_item in worn_items:
        events.append({
            'title': worn_item.item.name,
            'start': worn_item.date.isoformat(),
            'item_id': worn_item.item.id,
            'image': worn_item.item.image.url if worn_item.item.image else None,
        })

    return JsonResponse({'events': events})

def log_worn_items(request):
    if request.method == 'POST':
        selected_date = request.POST['date']
        item_ids = request.POST.getlist('item_ids')

        for item_id in item_ids:
            item = Item.objects.get(id=item_id)
            WornItem.objects.create(item=item, date=selected_date)
            item.wear_count += 1
            item.save()

        return JsonResponse({'success': True})

# home page
def home(request):
    return render(request, "home.html")

# closet page
def closet_view(request):
    items = Item.objects.prefetch_related('color')  # Optimize query with prefetch_related
    for item in items:
        # Safely extract color names into a separate attribute
        item.color_names = [color.name for color in item.color.all()] if item.color.exists() else []

    brands = Brand.objects.all()
    colors = Color.objects.all()
    categories = Category.objects.filter(parent=None)

    return render(request, 'closet.html', {
        'items': items,
        'brands': brands,
        'colors': colors,
        'categories': categories,
    })



# add item page - accessed in the closet page
def add_item(request):
    # retrieve item data
    if request.method == 'POST':
        name = request.POST.get('name', None)
        category_id = request.POST.get('subcategory', None)
        brand_name = request.POST.get('brand', None)
        color_id = request.POST.get('color', None)  # Get the color ID or None if not selected
        price = request.POST.get('price', None)  # Get price or None if not provided

        # handle brand creation or selection (optional)
        brand = None
        if brand_name:
            brand, _ = Brand.objects.get_or_create(name=brand_name)



        # convert price to float if needed
        price = float(price) if price else None

        # handle category
        category = None
        if category_id:
            category = Category.objects.get(id=category_id)

        # handle picture upload
        image = request.FILES.get("image")

        # create item
        item = Item.objects.create(
            name=name, 
            category=category, 
            brand=brand, 
            price=price,
            image=image
        )
        # item.color.add(color)
        if color_id:  # Check if a color was selected
            color = Color.objects.get(id=color_id)
            item.color.add(color)  # Add the color to the item

        messages.success(request, "Item added successfully!")

        return redirect("closet")

    categories = Category.objects.filter(parent=None)  # Top-level categories
    brands = Brand.objects.all()
    colors = Color.objects.all()  # Fetch all colors
    return render(request, 'add_item.html', {
        'categories': categories,
        'brands': brands,
        'colors': colors,  # Pass colors to the template
    })

def get_item(request, item_id):
    item = Item.objects.get(id=item_id)
    data = {
        'id': item.id,
        'name': item.name,
        'brand': {'id': item.brand.id, 'name': item.brand.name} if item.brand else None,
        'color': [color.name for color in item.color.all()],
        'price': item.price,
        'category': {'id': item.category.id, 'name': item.category.name} if item.category else None,
        'image': item.image.url if item.image else None,
    }
    return JsonResponse(data, safe=False)

def edit_item(request):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        item = Item.objects.get(id=item_id)

        item.name = request.POST.get('name', item.name)
        brand_name = request.POST.get('brand', None)
        if brand_name:
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            item.brand = brand

        price = request.POST.get('price', None)
        item.price = float(price) if price else None


        category_id = request.POST.get('category')
        if category_id:
            item.category = Category.objects.get(id=category_id)

        color_names = request.POST.get('color', '').split(', ')
        item.color.clear()
        for color_name in color_names:
            color, _ = Color.objects.get_or_create(name=color_name)
            item.color.add(color)

        if 'image' in request.FILES:
            item.image = request.FILES['image']

        item.save()

        messages.success(request, "Item edited successfully!"
                         )
        return redirect('closet')

def delete_item(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            item_id = data.get('item_id')

            if not item_id:
                return HttpResponseBadRequest("Item ID is required.")

            item = get_object_or_404(Item, id=item_id)
            item.delete()
            return JsonResponse({'success': True, 'message': f'Item {item_id} deleted successfully.'})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data.")
    return HttpResponseBadRequest("Invalid request method.")



def get_subcategories(request, parent_id=None):
    if parent_id is not None:
        subcategories = Category.objects.filter(parent_id=parent_id)
    else:
        subcategories = Category.objects.filter(parent=None)  # Top-level categories

    logger.debug(f"Fetched subcategories for parent_id={parent_id}: {subcategories}")

    data = {
        'subcategories': [
            {'id': cat.id, 'name': cat.name, 'selected': False} for cat in subcategories
        ]
    }
    return JsonResponse(data)




def get_category_path(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    path = []
    while category:
        siblings = Category.objects.filter(parent=category.parent).values('id', 'name')
        siblings_with_selected = [
            {'id': sibling['id'], 'name': sibling['name'], 'selected': sibling['id'] == category.id}
            for sibling in siblings
        ]
        path.insert(0, siblings_with_selected)  # Add sibling categories at each level
        category = category.parent
    return JsonResponse({'path': path})




def calendar(request):
    return render(request, "calendar.html")