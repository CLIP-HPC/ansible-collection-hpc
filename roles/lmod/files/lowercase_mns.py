# flake8: noqa
##
# Copyright 2013-2017 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/easybuilders/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
Implementation of (default) EasyBuild module naming scheme.

:author: Kenneth Hoste (Ghent University)
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from easybuild.tools.module_naming_scheme.easybuild_mns import EasyBuildMNS


class LowerCaseMNS(EasyBuildMNS):
    def det_full_module_name(self, ec):
        return super().det_full_module_name(ec).lower()

    def is_short_modname_for(self, short_modname, name):
        return name.lower() in short_modname
