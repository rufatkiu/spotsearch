# -*- coding: utf-8 -*-
'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''

from pkg_resources import get_distribution, DistributionNotFound

try:
    VERSION_STRING = get_distribution("spot").version
except DistributionNotFound:
    VERSION_STRING = "0.0.0"

try:
    SPOT_VERSION, METADATA_VERSION = VERSION_STRING.split("+")
except ValueError:
    SPOT_VERSION = VERSION_STRING
    METADATA_VERSION = ""
