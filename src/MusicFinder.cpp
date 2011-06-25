#include "MusicFinder.hpp"
#include <QRegExp>

namespace UDJ{


QList<Phonon::MediaSource> MusicFinder::findMusicInDir(const QString& musicDir){
  QList<Phonon::MediaSource> toReturn;
  QDir dir(musicDir);
  QFileInfoList potentialFiles = dir.entryInfoList(QDir::Dirs| QDir::Files | QDir::NoDotAndDotDot);
  QFileInfo currentFile;
  for(int i =0; i < potentialFiles.size(); ++i){
    currentFile = potentialFiles[i];
    if(currentFile.isFile() && isMusicFile(currentFile)){
      toReturn.append(Phonon::MediaSource(currentFile.absoluteFilePath()));
    }
    else if(currentFile.isDir()){
      toReturn.append(findMusicInDir(dir.absoluteFilePath(currentFile.absoluteFilePath())));
    }
  }
  return toReturn;
}

bool MusicFinder::isMusicFile(const QFileInfo& file){
  return getMusicFileMatcher().exactMatch(file.fileName());
}


} //end namespace
