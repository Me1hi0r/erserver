from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from panel import views as v

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', v.log_in),
    path('accounts/<str:action>/', v.authentification),

    path('panel', v.panel),
    path('sound', v.sound),
    path('config', v.config),
    path('config/<str:action>', v.config),

    path('sound/reset', v.reset_sound),
    path('sound/<str:sound_type>', v.sound_list),
    path('sound/<str:sound_type>/<int:riddle>', v.sound_list),

    path('data', v.data),
    path('debug', v.debug),
    path('upload_sound', v.upload_sound),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
