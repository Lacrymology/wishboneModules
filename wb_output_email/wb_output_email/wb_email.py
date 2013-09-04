#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpclient.py
#
#  Copyright 2013 Jelle Smet development@smetj.net
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone import Actor
from gevent import monkey; monkey.patch_socket()
from email.mime.text import MIMEText
from gevent import sleep
import smtplib

class Email(Actor):
    '''**A Wishbone module which sends out emails from incoming events.**

    Sends emails to a MTA using a provided template.

    Parameters:

        - name (str):           The instance name when initiated.

        - mta (string):         The address:port of the MTA to submit the
                                mail to.
                                (default: localhost:25)

        - key (string):         The header key containing the address information.
                                Default: self.name

        - success (bool):       When true stores the event in success queue if
                                send successfully.
                                default: False

        - failed (bool):        When true stores the event in failed queue if
                                not send successfully.
                                default: False


    Queues:

        - inbox:    Outgoing events

        - success:  Successful events

        - failed:   Failed events
    '''

    def __init__(self, name, mta="localhost:25", key=None, success=False, failed=False):
        Actor.__init__(self, name)
        self.name=name
        self.mta=mta
        if key==None:
            self.key = self.name
        else:
            self.key = key
        self.success=success
        self.failed=failed
        self.logging.info('Initialiazed.')
        if self.success == True:
            self.createQueue("success")
        if self.failed == True:
            self.createQueue("failed")

    def consume(self, event):
        if self.key not in event["header"]:
            self.logging.warn("Event received without <%s> header key. Purged"%(self.key))
            return
        for item in ["from","to","subject","template"]:
            if item not in event["header"][self.key]:
                self.logging.warn("Event received without <%s> header key. Purged"%(item))
                return
        try:
            message = msg=MIMEText(str(event["data"]))
            message["Subject"] = event["header"][self.key]["subject"]
            message["From"] = event["header"][self.key]["from"]
            message["To"] = ",".join(event["header"][self.key]["to"])

            mta=smtplib.SMTP(self.mta)
            mta.sendmail(event["header"][self.key]["from"],
                event["header"][self.key]["to"],
                message.as_string()
            )

            if self.success==True:
                self.queuepool.success.put(event)

        except Exception as err:
            if self.failed==True:
                self.logging.warn("Failed to send mail. Event moved to failed queue. Reason: %s."%(err))
                self.queuepool.failed.put(event)
            else:
                self.logging.warn("Failed to send mail. Reason: %s.  Waiting for a second and retry."%(err))
                self.queuepool.inbox.rescue(event)
                sleep(1)