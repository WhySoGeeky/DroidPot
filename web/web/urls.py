from django.conf.urls import patterns, include, url
from django.contrib import admin
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'dashboard.views.index', name="index"),
    url(r'^new_session$', 'dashboard.views.new_session', name="new_session"),
    url(r'^monitoring/', 'dashboard.views.monitoring', name="monitoring"),
    url(r'^profiles/', 'dashboard.views.profiles', name="profiles"),
    url(r'^summary/([0-9]+)$', 'dashboard.views.summary', name="summary"),
    url(r'^initialize/([0-9]+)$', 'dashboard.views.initialize', name="initialize"),
    url(r'^copy_config/([0-9]+)/([0-9]+)$', 'dashboard.views.copy_config', name="copy_config"),
    url(r'^upload_sample/([0-9]+)$', 'dashboard.views.upload_sample', name="upload_sample"),
    url(r'^report/([0-9]+)$', 'dashboard.views.report', name="report"),
    url(r'^analysis_duration/([0-9]+)$', 'dashboard.views.analysis_duration', name="analysis_duration"),
    url(r'^end_session/([0-9]+)$', 'dashboard.views.end_session', name="end_session"),
    url(r'^select_device/([a-zA-Z0-9_]+)/([0-9]+)$', 'dashboard.views.select_device', name="select_device"),
    url(r'^progress/([0-9]+)$', 'dashboard.views.progress', name="progress"),
    url(r'^check_time/([0-9]+)$', 'dashboard.views.check_time', name="check_time"),
    url(r'^processing/([0-9]+)$', 'dashboard.views.processing', name="processing"),
    url(r'^report_details/([0-9]+)$', 'dashboard.views.report_details', name="report_details"),


)




