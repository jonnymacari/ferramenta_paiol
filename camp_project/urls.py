from django.contrib import admin
from django.urls import path, include  # ⬅️ precisamos do include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ⬅️ agora tudo que era da app core está separado
    path('temporadas/', include('temporadas.urls')),
]
