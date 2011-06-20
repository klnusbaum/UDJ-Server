#include "MusicLibrary.hpp"

namespace UDJ{


MusicLibrary::MusicLibrary(){

}

MusicLibrary::~MusicLibrary(){

}

bool MusicLibrary::open(){
  db = QSqlDatabase::addDatabase("QSQLITE", getMusicDBConnectionName()); 
  QDir dbDir(QDesktopServices::storageLocation(QDesktopServices::DataLocation));  if(!dbDir.exists()){
    //TODO handle if this fails
    dbDir.mkpath(dbDir.absolutePath());
  }
  db.setName(dbDir.absoluteFilePath(getMusicDBName()));
  return db.open(); 
}

const QSqlDatabase& getDatabase() const{
  return musicdb;
}


} //end namespace
