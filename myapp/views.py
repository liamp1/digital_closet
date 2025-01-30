from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Item, Category, Brand, Color, WornItem
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Max, Count
from datetime import datetime

logger = logging.getLogger(__name__)

def get_dashboard_data(request):
    if request.method == 'GET':
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        # Count unique days with logs in the current month
        total_outfits = WornItem.objects.filter(date__year=current_year, date__month=current_month).values('date').distinct().count()
        print(f"Total Outfits This Month (Unique Days): {total_outfits}")  # Debug log

        # Get the most worn item
        most_worn_item = (
            Item.objects.annotate(wear_count_max=Count('worn_logs'))
            .order_by('-wear_count')
            .first()
        )
        print(f"Most Worn Item: {most_worn_item}")  # Debug log

        # Prepare the response data
        data = {
            'total_outfits': total_outfits,
            'most_worn_item': {
                'id': most_worn_item.id if most_worn_item else None,
                'name': most_worn_item.name if most_worn_item else "No items yet",
                'image': most_worn_item.image.url if most_worn_item and most_worn_item.image else None,
                'wear_count': most_worn_item.wear_count if most_worn_item else 0,
            },
        }
        print(f"Response Data: {data}")  # Debug log
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




def calendar_view(request):
    items = Item.objects.annotate(wear_count_max=Max('wear_count')).order_by('-wear_count')

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Count the total number of WornItem logs for the current month
    total_events = WornItem.objects.filter(date__year=current_year, date__month=current_month).count()

    most_frequent_item = items.first() if items else None

    #print(f"DEBUG: Items in Closet: {[item.name for item in items]}")  # Debug log
    return render(request, 'calendar.html', {'items': items, 'most_frequent_item': most_frequent_item, 'total_events': total_events})

def get_calendar_data(request):
    start_date = request.GET.get('start', '').split('T')[0]
    end_date = request.GET.get('end', '').split('T')[0]

    #print(f"Start Date: {start_date}, End Date: {end_date}")  # Debug log
    worn_items = WornItem.objects.filter(date__range=[start_date, end_date]).select_related('item')

    events = []
    for worn_item in worn_items:
        #print(f"Worn Item: {worn_item.item.name}, Date: {worn_item.date}")  # Debug log
        events.append({
            'title': worn_item.item.name,
            'start': worn_item.date.isoformat(),
            'item_id': worn_item.item.id,
            'image': worn_item.item.image.url if worn_item.item.image else None,
        })

    #print(f"Events Sent to Calendar: {events}")  # Debug log
    return JsonResponse({'events': events})



def log_worn_items(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_date = data.get('date')
            item_ids = data.get('item_ids', [])

            print(f"Selected Date: {selected_date}")  # Debug log
            print(f"Item IDs: {item_ids}")  # Debug log

            if not selected_date:
                return JsonResponse({'success': False, 'message': 'Date is missing.'}, status=400)

            # Remove all logs if no items are selected
            if not item_ids:
                logs_to_remove = WornItem.objects.filter(date=selected_date)
                for log in logs_to_remove:
                    log.item.wear_count = F('wear_count') - 1  # Decrement wear count
                    log.item.save()
                    log.delete()
                return JsonResponse({'success': True, 'message': 'All items removed for the selected date.'})

            # Fetch all existing WornItems for the date
            existing_logs = WornItem.objects.filter(date=selected_date)
            print(f"Existing Logs for {selected_date}: {[log.item.id for log in existing_logs]}")  # Debug log

            # Find items to remove (items that are no longer in the selection)
            existing_item_ids = existing_logs.values_list('item_id', flat=True)
            items_to_remove = set(existing_item_ids) - set(item_ids)
            print(f"Items to remove: {items_to_remove}")  # Debug log

            # Remove logs and decrement wear count
            for item_id in items_to_remove:
                item = Item.objects.get(id=item_id)
                WornItem.objects.filter(item=item, date=selected_date).delete()
                item.wear_count = F('wear_count') - 1  # Decrement wear_count
                item.save()

            # Add new items (items that are not already logged)
            items_to_add = set(item_ids) - set(existing_item_ids)
            print(f"Items to add: {items_to_add}")  # Debug log

            for item_id in items_to_add:
                item = Item.objects.get(id=item_id)
                WornItem.objects.create(item=item, date=selected_date)
                item.wear_count = F('wear_count') + 1  # Increment wear_count
                item.save()

            return JsonResponse({'success': True, 'message': 'Items logged successfully.'})

        except Exception as e:
            print(f"Error: {e}")  # Debug log
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)





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




# def calendar(request):
#     return render(request, "calendar.html")