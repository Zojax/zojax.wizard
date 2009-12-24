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
import unittest, os
from persistent import Persistent
from zope import interface, schema
from zope.testing import doctest
from zope.location import Location
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite
from zope.app.rotterdam import Rotterdam
from zojax.layoutform.interfaces import ILayoutFormLayer


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


wizardLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'wizardLayer', allow_teardown=True)


class IPerson(interface.Interface):

    name = schema.TextLine(
        title=u'Name',
        required = True)

    age = schema.Int(
        title=u'Age',
        description=u"The person's age.",
        min=0,
        default=20,
        required = False)


class IJob(interface.Interface):

    title = schema.TextLine(
        title = u'Title',
        required = True)


class Person(Persistent, Location):
    interface.implements(IPerson, IJob)


def test_suite():
    form = FunctionalDocFileSuite(
        "tests.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    form.layer = wizardLayer

    return unittest.TestSuite((form,))
