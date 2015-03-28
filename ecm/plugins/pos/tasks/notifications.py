# Copyright (c) 2015 Nicholas Steicke
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2015 03 27"
__author__ = 'Nicholas Steicke <nicholas.steicke@narthollis.net>'

import logging
import json
import datetime

import pytz
import requests

from django.conf import settings
from django.core.mail import send_mail

from ecm.plugins.pos.models import POS, POSNotification
from ecm.apps.hr.models import Role, RoleType
from ecm.apps.common.auth import get_directors_group

from ecm.plugins.pos.views.pos_list import getFuelValue

logger = logging.getLogger(__name__)

# TODO: Localisation
BASE_URL = ('https://' if settings.USE_HTTPS else 'http://') + settings.EXTERNAL_HOST_NAME


TEMPLATES = {
    'fuel': {
        'title':  "POS Low Fuel %(location)s",
        'body': "The POS %(location)s (%(name)s) has less than %(time)s fuel remaining."
    },
    'reinforce': {
        'title':  "POS Reinforced %(location)s",
        'body': "The POS %(location)s (%(name)s) has been reinforced. It will exit at %(time)s."
    }
}


class Email(object):
    def __init__(self):
        pass

    def _make_details(self, time_left, pos):
        return {
            'location': pos.moon if pos.moon else pos.moon_id,
            'name': pos.custom_name,
            'time': time_left
        }

    def send(self, template, to, time_left, pos):
        details = self._make_details(time_left, pos)
        send_mail(
            template['title'] % details,
            (template['body'] % details) + '\t\n\r\n' + BASE_URL + pos.url,
            settings.DEFAULT_FROM_EMAIL,
            [to]
        )

        return 'email'


    def dismiss(self, notification):
        notification.dismissed = True
        notification.save()
        return True


class Pushbullet(Email):

    def __init__(self, key):
        super(Pushbullet, self).__init__()

        from requests import Session

        self.session = Session()
        self.session.headers.update({
            'Authorization:':  'Bearer ' + key,
            'Content-Type:': 'application/json'
        })

    def send(self, template, to, time_left, pos):
        details = self._make_details(time_left, pos)

        resp = self.session.post(
            'https://api.pushbullet.com/v2/pushes',
            data=json.dumps({
                'email': to,
                'type': 'link',
                'url': BASE_URL + pos.url,
                'body': template['body'] % details,
                'title': template['title'] % details
            })
        )

        result = False
        if resp.status_code != requests.codes.ok:
            logger.warning("Failed sending notification, " + resp.text)
        else:
            return resp.json()['iden']

        resp.close()
        return result

    def dismiss(self, notification):
        # Just in case someone changes from email to pushbullet after some notifications
        # Have been generated
        if notification.pushbullet_id == "email":
            return Email().dismiss(notification)

        resp = self.session.post(
            'https://api.pushbullet.com/v2/pushes/' + notification.pushbullet_id,
            data='{"dismissed": true}'
        )

        result = False
        if resp.status_code == requests.codes.ok:
            notification.dismissed = True
            notification.save()
            result = True
        else:
            logger.warning("Failed sending notification, " + resp.text)

        resp.close()
        return result


def notify():
    """
    Loop over all PoS structures and sent out notifications for low fuel etc.

    Send 1 alert to each pos manager when fuel is under:
        48, 24, 12, 3, 2, 1
    And then once per hour when fuel is at 0

    """

    if settings.PUSHBULLET_KEY:
        sender = Pushbullet(settings.PUSHBULLET_KEY)
    else:
        sender = Email()

    # Build a list of all users with POS roles to alert when a POS is at 0 hours left
    general_role = RoleType.objects.get(typeName="roles")

    starbase_fuel = Role.objects.get(roleName="roleStarbaseConfig", roleType=general_role)
    starbase_config = Role.objects.get(roleName="roleStarbaseConfig", roleType=general_role)

    additional_at_zero = set()
    for member in starbase_fuel.members_through_titles(with_direct_roles=True):
        try:
            additional_at_zero.add(member.owner.email)
        except Exception, e:
            pass
    for member in starbase_config.members_through_titles(with_direct_roles=True):
        try:
            additional_at_zero.add(member.owner.email)
        except Exception, e:
            pass

    directors = get_directors_group().user_set.values_list('email', flat=True)

    offline_cutoff = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=14)

    for pos in POS.objects.all():
        # If the POS is reinforced send an email to all directors
        if pos.state == 3:
            for email in directors:
                foreign_iden = sender.send(
                    TEMPLATES['reinforce'],
                    email,
                    pos.state_timestamp.strftime('%H:%M, %d %b'),
                    pos
                )

                POSNotification(
                    type=0,
                    pos=pos,
                    internal_ident='re' + datetime.datetime.now().strftime('%Y%m%d%H'),
                    to=email,
                    foreign_iden=foreign_iden
                ).save()
        else:
            for notification in POSNotification.objects.filter(type=0, pos=pos, dismissed=False):
                sender.dismiss(notification)

        # Do not check fuel for unanchorded
        if pos.state == 0:
            continue

        # If the POS is offline, and has been for more than 14 days,
        #   do not send any notifications
        if pos.state == 1:
            if pos.state_timestamp < offline_cutoff:
                for notification in POSNotification.objects.filter(type=1, pos=pos, dismissed=False):
                    sender.dismiss(notification)
                continue

        hours_left = getFuelValue(pos, pos.fuel_type_id, 'hours_int')

        if hours_left <= 0:
            hours_left = 0
        elif hours_left <= 1:
            hours_left = 1
        elif hours_left <= 2:
            hours_left = 2
        elif hours_left <= 3:
            hours_left = 3
        elif hours_left <= 12:
            hours_left = 12
        elif hours_left <= 24:
            hours_left = 24
        elif hours_left <= 48:
            hours_left = 48
        else:
            # If the POS has been fulled, lets make sure we dismiss all of the notifications
            #  this will help save other POS managers needing to login
            for notification in POSNotification.objects.filter(type=1, pos=pos, dismissed=False):
                sender.dismiss(notification)
            continue

        if hours_left <= 48:
            # If time left is zero we send out notifications once every hour,
            #   so we store the time left as the current time
            internal_ident = hours_left if hours_left > 0 else datetime.datetime.now().strftime('%Y%m%d%H')
            current_notification = POSNotification.objects.filter(
                type=1,
                pos=pos,
                dismissed=False,
                internal_ident=internal_ident
            )

            if len(current_notification) == 0:
                to_notify = set(pos.operators.values_list('email', flat=True))

                # If this POS has run dry, _or_ if there are no configured operators for this POS
                # then alert everyone with POS Fuel or Config roles
                if hours_left <= 0 or len(to_notify) == 0:
                    to_notify = to_notify | additional_at_zero

                logger.info("Sending %s fuel notification for %s to [%s]" % (
                    hours_left,
                    str(pos),
                    ', '.join(to_notify))
                )

                for email in to_notify:
                    foreign_iden = sender.send(
                        TEMPLATES['fuel'],
                        email,
                        '%s hours' % (hours_left,),
                        pos
                    )
                    POSNotification(
                        type=1,
                        pos=pos,
                        internal_ident=internal_ident,
                        to=email,
                        foreign_iden=foreign_iden
                    ).save()
