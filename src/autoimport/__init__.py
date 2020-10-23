"""Python program to automatically import missing python libraries.

Functions:
    fix_code: Fix python source code to correct missed or unused import statements.

    fix_files: Fix the python source code of a list of files.
"""

# Copyright (C) 2020 Lyz <lyz-code-security-advisories@riseup.net>
# This file is part of Autoimport.
#
# Autoimport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Autoimport is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Autoimport.  If not, see <http://www.gnu.org/licenses/>.

from .services import fix_code, fix_files  # noqa W0611
