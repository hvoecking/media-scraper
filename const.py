#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  const.py
#  
#  Copyright 2013 Heye Vöcking <heye.voecking at gmail.com>
#    
#  This program is distributed WITHOUT ANY WARRANTY!
#  I am happy if you want to use my code (or parts of it) in your 
#  project. So if you do, please contact me first before publishing
#  your code!
#  
#  The code in this class was inspired by: http://code.activestate.com/recipes/65207-constants-in-python/?in=user-97991
#  

import sys

class _const:
    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const(%s)"%name)
        self.__dict__[name]=value

sys.modules[__name__]=_const()
