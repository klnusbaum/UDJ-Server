SET(UDJ_SRCS 
  main.cpp 
  MetaWindow.cpp 
  MusicFinder.cpp 
  SettingsWidget.cpp 
  MusicLibrary.cpp
)

SET(UDJ_HDRS 
  MusicFinder.hpp
  MusicLibrary.hpp
)

SET(UDJ_MOC_HDRS 
  MetaWindow.hpp 
  SettingsWidget.hpp
)

QT4_WRAP_CPP(MOC_SRCS ${UDJ_MOC_HDRS})

set(QT_USE_PHONON TRUE)
set(QT_USE_QTSQL TRUE)
INCLUDE(${QT_USE_FILE})
ADD_DEFINITIONS(${QT_DEFINITIONS})

ADD_EXECUTABLE(UDJ ${UDJ_SRCS} ${MOC_SRCS} ${UDJ_MOD_HDRS} ${UDJ_HDRS})
TARGET_LINK_LIBRARIES(UDJ ${QT_LIBRARIES})
