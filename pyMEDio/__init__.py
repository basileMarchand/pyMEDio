#==============================================================================
# Copyright (C) 2016 Marchand Basile                                  
#                                                                     
# This file is part of pyMEDio  
#                                                                     
# pyMEDio is free software: you can redistribute it and/or modify   
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or   
# any later version.                           
#                                                               
# pyMEDio is distributed in the hope that it will be useful,   
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
# GNU General Public License for more details.
#                                
# You should have received a copy of the GNU General Public License 
# along with pyPointer.  If not, see <http://www.gnu.org/licenses/>   
#==============================================================================          
#----------------------------------      
# package    : pyMEDio     
# file       : __init__.py                                                                                                  
# content    :                                                                         
# author     : Basile Marchand (basile.marchand@gmail.com)                                                                     
# date       : 17-07-2016                                                     
#----------------------------------      


__all__=['MEDWriter', 'MEDReader']

from .writer import MEDWriter
from .reader import MEDReader
from .object_definition import Mesh, Field

import logging

logging.basicConfig(level=logging.INFO)


def verbose():
    logging.getLogger("pyMEDio.reader").setLevel(logging.DEBUG)
    logging.getLogger("pyMEDio.writer").setLevel(logging.DEBUG)

def quiet():
    logging.getLogger("pyMEDio.reader").setLevel(logging.ERROR)
    logging.getLogger("pyMEDio.writer").setLevel(logging.ERROR)


