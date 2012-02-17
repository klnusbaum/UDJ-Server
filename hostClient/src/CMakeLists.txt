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


configure_file(
  "${PROJECT_SOURCE_DIR}/src/ConfigDefs.hpp.in"
  "${PROJECT_BINARY_DIR}/src/ConfigDefs.hpp"
)

SET(UDJ_SRCS 
  main.cpp 
  PlaybackWidget.cpp
  MetaWindow.cpp 
  MusicFinder.cpp 
  SettingsWidget.cpp 
  DataStore.cpp
  ActivePlaylistView.cpp
  LibraryView.cpp
	UDJServerConnection.cpp
  JSONHelper.cpp
  qt-json/json.cpp
  LoginWidget.cpp
  ActivityList.cpp
  EventWidget.cpp
  CreateEventWidget.cpp
  EventDashboard.cpp
  WidgetWithLoader.cpp
  AvailableMusicView.cpp
  EventGoersView.cpp
  SongListView.cpp
  MusicModel.cpp
  LoginDialog.cpp
  simpleCrypt/simplecrypt.cpp
  CommErrorHandler.cpp
)

SET(UDJ_HDRS 
  MusicFinder.hpp
	ConfigDefs.hpp
  JSONHelper.hpp
  Utils.hpp
  qt-json/json.h
  simpleCrypt/simplecrypt.h
)

SET(UDJ_MOC_HDRS 
  MetaWindow.hpp 
  SettingsWidget.hpp
  DataStore.hpp
  ActivePlaylistView.hpp
  LibraryView.hpp
	DifferenceSpinner.hpp
	UDJServerConnection.hpp
  LoginWidget.hpp
  ActivityList.hpp
  PlaybackWidget.hpp
  EventWidget.hpp
  CreateEventWidget.hpp
  EventDashboard.hpp
  WidgetWithLoader.hpp
  AvailableMusicView.hpp
  EventGoersView.hpp
  SongListView.hpp
  MusicModel.hpp
  LoginDialog.hpp
  CommErrorHandler.hpp
)

include_directories("${PROJECT_BINARY_DIR}/src")

QT4_WRAP_CPP(MOC_SRCS ${UDJ_MOC_HDRS})

INCLUDE(${QT_USE_FILE})
ADD_DEFINITIONS(${QT_DEFINITIONS})

SET(UDJ_DEP_LIBS ${QT_LIBRARIES} ${QT_PHONON_LIBRARY} ${TAGLIB})

IF(CMAKE_HOST_APPLE)

ADD_EXECUTABLE(UDJ MACOSX_BUNDLE ${UDJ_SRCS} ${MOC_SRCS} ${UDJ_MOD_HDRS} ${UDJ_HDRS})
INSTALL(TARGETS UDJ BUNDLE DESTINATION bin )


ELSEIF(CMAKE_HOST_WIN32)



	
SET(CMAKE_MFC_FLAGE 2)
ADD_EXECUTABLE(UDJ WIN32 ${UDJ_SRCS} ${MOC_SRCS} ${UDJ_MOD_HDRS} ${UDJ_HDRS})
INSTALL(TARGETS UDJ RUNTIME DESTINATION bin )
SET(UDJ_DEP_LIBS ${UDJ_DEP_LIBS} ${QT_QTMAIN_LIBRARY})
ADD_DEFINITIONS(-DQT_DLL)

#We need the actual dll files on windows because they have to be bundled
#with our installer. We can't just bundle the static libs we may have used
#when compiling. So dlls in this case don't necessarily have to 
#be the actual libraries we built against (with regards to just taglib and zlib)
#why we have to do this, I have no idea. It's all weird shit to me. I wish I
#knew more about windows dev. All I know is that when I build against my
#tab.lib and zlib1.lib libraries but include the dlls with the installer things
#seem to work.
IF(NOT TAGLIB_DLL_FILE)
message(FATAL_ERROR "Must specify the absolute file path to the taglib dll")
ENDIF(NOT TAGLIB_DLL_FILE)

IF(NOT ZLIB_DLL_FILE)
message(FATAL_ERROR "Must specify the absolute file path to the zlib dll")
ENDIF(NOT ZLIB_DLL_FILE)


GET_FILENAME_COMPONENT(QT_DLL_PATH_tmp ${QT_QMAKE_EXECUTABLE} PATH)
GET_FILENAME_COMPONENT(TAG_DLL_NAME ${TAGLIB_DLL_FILE} NAME)
GET_FILENAME_COMPONENT(ZLIB_DLL_NAME ${ZLIB_DLL_FILE} NAME)


#IF(CMAKE_BUILD_TYPE STREQUAL "Debug")
CONFIGURE_FILE(${QT_DLL_PATH_tmp}/phonond4.dll 
  ${PROJECT_BINARY_DIR}/phonond4.dll COPYONLY)
CONFIGURE_FILE(${QT_DLL_PATH_tmp}/QtGuid4.dll 
  ${PROJECT_BINARY_DIR}/QtGuid4.dll COPYONLY)
CONFIGURE_FILE(${QT_DLL_PATH_tmp}/QtCored4.dll 
  ${PROJECT_BINARY_DIR}/QtCored4.dll COPYONLY)
CONFIGURE_FILE(${QT_DLL_PATH_tmp}/QtSqld4.dll 
  ${PROJECT_BINARY_DIR}/QtSqld4.dll COPYONLY)
CONFIGURE_FILE(${QT_DLL_PATH_tmp}/QtNetworkd4.dll 
  ${PROJECT_BINARY_DIR}/QtNetworkd4.dll COPYONLY)
CONFIGURE_FILE(${TAGLIB_DLL_FILE} 
  ${PROJECT_BINARY_DIR}/${TAG_DLL_NAME} COPYONLY)
CONFIGURE_FILE(${ZLIB_DLL_FILE} 
  ${PROJECT_BINARY_DIR}/${ZLIB_DLL_NAME} COPYONLY)

INSTALL(FILES ${PROJECT_BINARY_DIR}/phonond4.dll DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/QtGuid4.dll DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/QtCored4.dll DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/QtSqld4.dll DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/QtNetworkd4.dll DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/${TAG_DLL_NAME} DESTINATION bin)
INSTALL(FILES ${PROJECT_BINARY_DIR}/${ZLIB_DLL_NAME} DESTINATION bin)

#INSTALL(FILES ${QT_DLL_PATH_tmp}/phonond4.dll 
#  DESTINATION bin)
#INSTALL(FILES ${QT_DLL_PATH_tmp}/QtGuid4.dll 
#  DESTINATION bin)
#INSTALL(FILES ${QT_DLL_PATH_tmp}/QtCored4.dll 
#  DESTINATION bin)
#INSTALL(FILES ${QT_DLL_PATH_tmp}/QtSqld4.dll 
#  DESTINATION bin)
#INSTALL(FILES ${QT_DLL_PATH_tmp}/QtNetworkd4.dll 
#  DESTINATION bin)
#INSTALL(FILES ${TAGLIB_DLL_FILE} DESTINATION bin)
#INSTALL(FILES ${ZLIB_DLL_FILE} DESTINATION bin)

#ELSE(CMAKE_BUILD_TYPE STREQUAL "Debug")
#INSTALL(FILES ${QT_DLL_PATH_tmp}/phonon4.dll 
#  DESTINATION bin)
#ENDIF(CMAKE_BUILD_TYPE STREQUAL "Debug")




ELSE(CMAKE_HOST_APPLE)

ADD_EXECUTABLE(UDJ ${UDJ_SRCS} ${MOC_SRCS} ${UDJ_MOD_HDRS} ${UDJ_HDRS})
INSTALL(TARGETS UDJ RUNTIME DESTINATION bin )


ENDIF(CMAKE_HOST_APPLE)


TARGET_LINK_LIBRARIES(UDJ ${UDJ_DEP_LIBS} )


SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "A collaborative music player")
SET(CPACK_PACKAGE_VENDOR "Bazaar Solutions")
SET(CPACK_PACKAGE_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
SET(CPACK_PACKAGE_VERSION_MAJOR "0")
SET(CPACK_PACKAGE_VERSION_MINOR "2")
SET(CPACK_PACKAGE_VERSION_PATCH "0")
SET(CPACK_PACKAGE_EXECUTABLES "UDJ" "UDJ")

INCLUDE(CPACK)
