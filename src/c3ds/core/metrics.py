import datetime
from typing import Optional

from django.apps import apps
from django.core.cache import cache
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client.registry import Collector

from c3ds.core.models import Display, BaseView, HTMLView, ImageView, VideoView, IFrameView, ScheduleView


class CustomCollector(Collector):
    def collect(self):
        # For some reason this is called two times during initialization where we don't want to do Database queries.
        # So we check if initialization is done, and if not just exist.
        if not apps.ready:
            return

        now = datetime.datetime.now(tz=datetime.UTC)
        online = GaugeMetricFamily('display_online', 'Online status of displays',
                                   labels=['display_slug'])
        ntp_offset = GaugeMetricFamily('display_ntp_offset', 'NTP time offset of displays',
                                       labels=['display_slug'])
        # ntp_latency = GaugeMetricFamily('display_ntp_latency',
        #                                 'Latency between NTP Server and displays', labels=['display_slug'])
        display_slugs = Display.objects.all().values_list('slug', flat=True)
        displays_online = 0
        for slug in display_slugs:
            last_heartbeat: Optional[datetime.datetime] = cache.get(Display.heartbeat_cache_key_for_slug(slug))
            is_online = last_heartbeat is not None and (now - last_heartbeat).total_seconds() < 60
            if is_online:
                displays_online += 1
            online.add_metric([slug], 1 if is_online else 0)

            display_ntp_offset: Optional[float] = cache.get(Display.ntp_offset_cache_key_for_slug(slug))
            if display_ntp_offset is not None:
                ntp_offset.add_metric([slug], display_ntp_offset)
        yield online
        yield ntp_offset
        yield GaugeMetricFamily('number_of_displays', 'Number of displays',
                                value=len(display_slugs))
        yield GaugeMetricFamily('number_of_displays_online', 'Number of displays currently online',
                                value=displays_online)

        view_count = GaugeMetricFamily('number_of_views', 'Number of views configured',
                                       labels=['type'])
        view_count.add_metric(['html'], HTMLView.objects.all().count())
        view_count.add_metric(['image'], ImageView.objects.all().count())
        view_count.add_metric(['video'], VideoView.objects.all().count())
        view_count.add_metric(['iframe'], IFrameView.objects.all().count())
        view_count.add_metric(['schedule'], ScheduleView.objects.all().count())
        yield view_count
        yield GaugeMetricFamily('number_of_views_total', 'Number of views configured',
                                value=BaseView.objects.all().count())

REGISTRY.register(CustomCollector())