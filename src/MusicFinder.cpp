/**
 * Copyright 2011 Kurtis L. Nusbaum
 * 
 * This file is part of UDJ.
 * 
 * UDJ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 * 
 * UDJ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
 */
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
