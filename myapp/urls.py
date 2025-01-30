from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # call home function from views if blank path
    path("", views.home, name="home"),
    #path("calendar/", views.calendar, name="calendar"),
    path("closet/", views.closet_view, name="closet"),

    path("closet/add-item/", views.add_item, name="add_item"),

    path('closet/get-item/<int:item_id>/', views.get_item, name='get_item'),
    path('closet/edit-item/', views.edit_item, name='edit_item'),
    path('closet/delete-item/', views.delete_item, name='delete_item'),
    path('closet/category-path/<int:category_id>/', views.get_category_path, name='get_category_path'),

    path('closet/subcategories/', views.get_subcategories, name='get_subcategories_root'),
    path('closet/subcategories/<int:parent_id>/', views.get_subcategories, name='get_subcategories'),

    path("calendar/", views.calendar_view, name="calendar"),
    path('calendar/data/', views.get_calendar_data, name='get_calendar_data'),
    path('calendar/log/', views.log_worn_items, name='log_worn_items'),
    path('calendar/dashboard-data/', views.get_dashboard_data, name='get_dashboard_data'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)