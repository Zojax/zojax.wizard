##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Castom Button Widget Implementation

$Id$
"""
from zope import interface, component

from z3c.form import interfaces, button
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.wizard.interfaces import IPreviousAction, IForwardAction


class BackButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, IPreviousAction)

    klass="z-wizard-previousbutton"


class ForwardButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, IForwardAction)

    klass="z-wizard-forwardbutton"
