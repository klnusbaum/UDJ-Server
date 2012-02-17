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
  COMPONENTS QtCore QtGui Phonon QtSql QtNetwork REQUIRED)

FIND_LIBRARY(TAGLIB "tag")
IF(NOT TAGLIB)
  MESSAGE(fatal_error "Could not find taglib")
ENDIF(NOT TAGLIB)

FIND_PATH(TAGLIB_HEADER_PATH "taglib/taglib.h")
IF(NOT TAGLIB_HEADER_PATH)
  message(FATAL_ERROR "Couldn't find path to taglib header")
ENDIF(NOT TAGLIB_HEADER_PATH)
include_directories("${TAGLIB_HEADER_PATH}/taglib")

set(UDJ_DEBUG_BUILD FALSE CACHE BOOL "Enables/Disables a debug build of UDJ")

IF(UDJ_DEBUG_BUILD)
  ADD_DEFINITIONS(-DUDJ_DEBUG_BUILD)
ENDIF(UDJ_DEBUG_BUILD)

set(GEOCODER_API_KEY "" CACHE STRING "The api key to user for the usc geocoder webservice")

set(SETTINGS_CRYPTO_KEY "" CACHE STRING "Must speicfy a settings crypto key")

IF(NOT GEOCODER_API_KEY)
  message(FATAL_ERROR "Must specify GEOCODER_API_KEY")
ENDIF(NOT GEOCODER_API_KEY)

IF(NOT SETTINGS_CRYPTO_KEY)
  message(FATAL_ERROR "Must specify SETTINGS_CRYPTO_KEY")
ENDIF(NOT SETTINGS_CRYPTO_KEY)

#IF(WIN32)
#INSTALL(FILES phonon4.dll DESTINATION bin)
#ENDIF(WIN32)

ADD_SUBDIRECTORY(src)
