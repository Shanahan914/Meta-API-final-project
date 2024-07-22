from django.contrib import admin
from .models import * 
from django.apps import apps

app = apps.get_app_config('LittleLemonAPI')
print(app)

# Register your models here.

for model_mame, model in app.models.items():
    admin.site.register(model)
                 