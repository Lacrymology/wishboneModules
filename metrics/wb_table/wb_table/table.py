#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  log.py
#  
#  Copyright 2013 Jelle Smet <development@smetj.net>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

import logging
from prettytable import PrettyTable
from os import system
from sys import stderr

class Table():
    def __init__(self):
        self.logging = logging.getLogger( 'Metrics module Log' )
        self.logging.info("Initiated")
    
    def do(self,data):
        self.logging.info(str(data))
        func_table = PrettyTable(["Instance", "Function", "Total time", "Hits per second","Hits","Average time"])
        func_table.align["Instance"] = "l"
        func_table.align["Function"] = "l"
        func_table.align["Total time"] = "r"
        func_table.align["Hits per second"] = "r"
        func_table.align["Hits"] = "r"
        func_table.align["Average time"] = "r"

        for instance in data["functions"]:
            for function in data["functions"][instance]:
                func_table.add_row([instance, function, data["functions"][instance][function]["total_time"], data["functions"][instance][function]["hits_per_sec"], data["functions"][instance][function]["hits"], data["functions"][instance][function]["avg_time"]])

        conn_table = PrettyTable(["Source","Destination","Hits"])
        conn_table.align["Source"] = "l"
        conn_table.align["Destination"] = "l"
        conn_table.align["Hits"] = "r"

        for connector in data["connectors"]:
            direction = connector.split("->")
            conn_table.add_row([direction[0],direction[1],data["connectors"][connector]])

        #todo: has to be done differently
        system('/usr/bin/clear')
        stderr.write ("Function metrics:\n%s\n\nConnector metrics:\n%s\n"%(func_table, conn_table))
