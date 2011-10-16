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

SET(UDJ_SRCS 
  main.cpp 
  PlaybackWidget.cpp
  MetaWindow.cpp 
  MusicFinder.cpp 
  SettingsWidget.cpp 
  MusicLibrary.cpp
  PlaylistView.cpp
  LibraryView.cpp
  PlaylistDelegate.cpp
	PlaylistModel.cpp
	UDJServerConnection.cpp
	PartiersView.cpp
  JSONHelper.cpp
  LibraryModel.cpp
  qt-json/json.cpp
  LoginWidget.cpp
  ActivityList.cpp
)

SET(UDJ_HDRS 
  MusicFinder.hpp
	ConfigDefs.hpp
  JSONHelper.hpp
  qt-json/json.h
)

SET(UDJ_MOC_HDRS 
  MetaWindow.hpp 
  SettingsWidget.hpp
  MusicLibrary.hpp
  PlaylistView.hpp
  LibraryView.hpp
  PlaylistDelegate.hpp
	PlaylistModel.hpp
	DifferenceSpinner.hpp
	UDJServerConnection.hpp
	PartiersView.hpp
  LibraryModel.hpp
  LoginWidget.hpp
  ActivityList.hpp
  PlaybackWidget.hpp
)

QT4_WRAP_CPP(MOC_SRCS ${UDJ_MOC_HDRS})

INCLUDE(${QT_USE_FILE})
ADD_DEFINITIONS(${QT_DEFINITIONS})

ADD_EXECUTABLE(UDJ ${UDJ_SRCS} ${MOC_SRCS} ${UDJ_MOD_HDRS} ${UDJ_HDRS})
TARGET_LINK_LIBRARIES(UDJ ${QT_LIBRARIES} ${QT_PHONON_LIBRARY})

