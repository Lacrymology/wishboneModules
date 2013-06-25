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

from gevent import monkey; monkey.patch_all()
from wishbone.toolkit import PrimitiveActor
from email.mime.text import MIMEText
from gevent import sleep, spawn
from Cheetah.Template import Template
from glob import glob
from os import path
import gevent_inotifyx as inotify
import smtplib
import logging



class EmailClient(PrimitiveActor):
    '''**A Wishbone IO module which sends out emails from incoming events.**

    Sends emails to a MTA using a provided template.

    Parameters:

        - name (str):   The instance name when initiated.
        - mta (string): The address:port of the MTA to submit the mail to.
                        (default: localhost:25)
        - template (string): The path to the template to use

    Header:

        - from (string):    The from address.
        - to (list):        A list of destinations.
        - subject (list):   The subject to use.
        - template (str):   The absolute path of the email template to use.

    Queues:

        - inbox:    Incoming events (dict).
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, templatedir="blah", mta="localhost:25", passthrough=False):
        PrimitiveActor.__init__(self, name)
        self.name=name
        self.mta=mta
        self.passthrough=passthrough
        self.logging = logging.getLogger( name )
        self.mailer=self.__setupMail(mta)
        self.templates=self.readDirectory(templatedir)
        spawn(self.monitorDirectory,templatedir)
        self.logging.info('Initialiazed.')

    def __setupMail(self, mta):
        return smtplib.SMTP(mta)

    def monitorDirectory(self, directory):
        '''Monitors the given directory for changes.'''
        while self.block() == True:
            try:
                fd = inotify.init()
                wb = inotify.add_watch(fd, directory, inotify.IN_CLOSE_WRITE+inotify.IN_DELETE)
                self.logging.info('Monitoring %s'%(directory))
                while self.block() == True:
                    events = inotify.get_events(fd)
                    self.templates = self.readDirectory(directory)
            except Exception as err:
                self.logging.error("There was a problem loading the email templates. Reason: %s"%(err))
                sleep(1)

    def readDirectory(self, directory):
        '''Reads the content of the given directory and creates a dict
        containing the templates.'''

        templates={}
        try:
            for filename in glob("%s/*.tmpl"%(directory)):
                f=open (filename,'r')
                self.logging.info('Loading template %s from directory %s'%(filename, directory))
                templates[path.basename(filename).replace(".tmpl","")]="".join(f.readlines())
                f.close()
        except Exception as err:
            self.logging.error("There was a problem loading the email templates. Reason: %s"%(err))

        return templates

    def consume(self, event):
        for item in ["from","to","subject","template"]:
            if item not in event["header"]:
                self.logging.warn("Event received without %s header key. Purged"%(item))
                return

        msg=self.constructEmail(event)

        while self.block()==True:
            try:
                self.mailer.sendmail(event["header"]["from"], event["header"]["to"], msg.as_string())
                break
            except Exception as err:
                self.mailer=self.__setupMail(self.mta)
                self.logging.warn("Failed to send mail. Reason: %s.  Waiting for a second and retry."%(err))
                sleep(1)
        if self.passthrough == True:
            self.putData(event, queue='outbox')

    def constructEmail(self, event):
        if not self.templates.has_key(event["header"]["template"]):
            msg=MIMEText(str(event["data"]))
            msg['Subject']="Warning. Unknown template name defined. "+event["header"]["subject"]
        else:
            try:
                body = Template(self.templates[event["header"]["template"]], searchList=event["data"])
            except Exception as err:
                self.logging.error('There was an error processing the template. Reason: %s'%(err))
                body = "There was an error processing the template. Reason: %s"%(err)
            msg=MIMEText(str(body))

            try:
                msg['Subject']=str(Template(event["header"]["subject"], searchList=event["data"]))
            except Exception as err:
                self.logging.error('There was an error processing the subject. Reason: %s'%(err))
                msg['Subject'] = event["header"]["subject"]

        msg['From']=event["header"]["from"]
        msg['To']=','.join(event["header"]["to"])
        return msg

    def shutdown(self):
        self.mailer.close()
        self.logging.info('Shutdown')
