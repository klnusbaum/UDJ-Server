#include "MusicFinder.hpp"
#include <QRegExp>

namespace UDJ{


QList<Phonon::MediaSource> MusicFinder::findMusicInDir(const QDir& musicDir){
  QList<Phonon::MediaSource> toReturn;
  QFileInfoList potentialFiles = musicDir.entryInfoList(
    QDir::Files | QDir::Dirs | QDir::Readable | QDir::NoDotAndDotDot);
  QFileInfo currentFile;
  for(int i =0; i < potentialFiles.size(); ++i){
    currentFile = potentialFiles[i];
    if(currentFile.isFile() && isMusicFile(currentFile)){
      toReturn.append(Phonon::MediaSource(currentFile.absoluteFilePath()));
    }
    else if(currentFile.isDir()){
      toReturn.append(findMusicInDir(QDir(currentFile.absoluteFilePath())));
    }
  }
  return toReturn;
}

bool MusicFinder::isMusicFile(const QFileInfo& file){
  return getMusicFileMatcher().exactMatch(file.fileName());
}


} //end namespace
