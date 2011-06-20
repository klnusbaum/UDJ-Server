#ifndef MUSIC_LIBRARY_HPP
#define MUSIC_LIBRARY_HPP


namespace UDJ{


class MusicLibrary{
public:
  MusicLibrary();
  ~MusicLibrary();
  bool open(); 
  const QSqlDatabase& getDatabase() const;
  static const QString& getMusicDBConnectionName(){
    static const QString musicDBConnectionName("musicdbConn");
    return musicDBConnectionName;
  }

  static const QString& getMusicDBName(){
    static const QString musicDBName("librarydb");
    return musicDBName;
  }

private:
  QSqlDatabase musicdb;
};


} //end namespace
#endif //MUSIC_LIBRARY_HPP
