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
"""

$Id$
"""
from zope import component, interface
from zope.traversing.browser import absoluteURL
from z3c.breadcrumb.browser import GenericBreadcrumb
from zojax.wizard.interfaces import IWizard


class WizardBreadcrumb(GenericBreadcrumb):
    component.adapts(IWizard, interface.Interface)

    @property
    def name(self):
        return self.context.label

    @property
    def url(self):
        return '%s/'%absoluteURL(self.context, self.request)
