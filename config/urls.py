"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.template.response import TemplateResponse
from mahsulotlar.models import Mahsulot
from hodimlar.models import Hodim
from sotuv.models import Sotuv

# Customize admin site
admin.site.site_header = "CRM Dashboard"
admin.site.site_title = "CRM Admin"
admin.site.index_title = "Boshqaruv Paneli"

# Save reference to original index method
_original_index = admin.site.index

# Custom admin index view with statistics
def admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    try:
        extra_context.update({
            'mahsulotlar_count': Mahsulot.objects.count(),
            'hodimlar_count': Hodim.objects.count(),
            'sotuvlar_count': Sotuv.objects.count(),
            'umumiy_narx': sum([float(m.narx) for m in Mahsulot.objects.all()]) if Mahsulot.objects.exists() else 0,
        })
    except Exception:
        # If there's any error, set defaults
        extra_context.update({
            'mahsulotlar_count': 0,
            'hodimlar_count': 0,
            'sotuvlar_count': 0,
            'umumiy_narx': 0,
        })
    # Call the original index method
    return _original_index(request, extra_context)

# Override admin index
admin.site.index = admin_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("main.urls")),
    path('hodimlar/', include('hodimlar.urls')),
    path('sotuv/', include('sotuv.urls')),
    path('mahsulotlar/', include('mahsulotlar.urls')),
]
