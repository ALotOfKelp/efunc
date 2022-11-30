#    __init__.py -- efunc module wrapper
#    Copyright © 2022 Iskander Boutel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY# without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import platform

if ("arm64" not in platform.platform().lower()) or platform.system() != "Darwin":
    raise SystemError("efunc is only compatible with arm-based darwin systems")

from .efunc import *
import warnings

warnings.filterwarnings("ignore", category = DeprecationWarning)