#
# Copyright 2011 Kurtis L. Nusbaum
# 
# This file is part of UDJ.
# 
# UDJ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# UDJ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with UDJ.  If not, see <http://www.gnu.org/licenses/>.

cmake_minimum_required(VERSION 2.6)
PROJECT(UDJ)
FIND_PACKAGE(Qt4 4.4.3 
  COMPONENTS QtCore QtGui QtPhonon QtSql QtNetwork REQUIRED)

#IF(NOT QT_PHONON_FOUND)
#message(FATAL_ERROR "Couldn't find Phonon module!")
#ENDIF(NOT QT_PHONON_FOUND)
#
#IF(NOT QT_QTSQL_FOUND)
#message(FATAL_ERROR "Couldn't find QtSql module!")
#ENDIF(NOT QT_QTSQL_FOUND)

set(UDJ_DEBUG_BUILD FALSE CACHE BOOL "Enables/Disables a debug build of UDJ")

IF(UDJ_DEBUG_BUILD)
  ADD_DEFINITIONS(-DUDJ_DEBUG_BUILD)
ENDIF(UDJ_DEBUG_BUILD)
  

ADD_SUBDIRECTORY(src)
