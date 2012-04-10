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
#include <phonon/backendcapabilities.h>
#include "ConfigDefs.hpp"

namespace UDJ{

QList<Phonon::MediaSource> MusicFinder::findMusicInDir(const QString& musicDir){
  QRegExp fileMatcher = getMusicFileMatcher();
  return findMusicInDirWithMatcher(musicDir, fileMatcher);
}

QList<Phonon::MediaSource> MusicFinder::findMusicInDirWithMatcher(
    const QString& musicDir, const QRegExp& fileMatcher)
{
  QList<Phonon::MediaSource> toReturn;
  QDir dir(musicDir);
  QFileInfoList potentialFiles = dir.entryInfoList(QDir::Dirs| QDir::Files | QDir::NoDotAndDotDot);
  QFileInfo currentFile;
  for(int i =0; i < potentialFiles.size(); ++i){
    currentFile = potentialFiles[i];
    if(currentFile.isFile() && fileMatcher.exactMatch(currentFile.fileName())){
      toReturn.append(Phonon::MediaSource(currentFile.absoluteFilePath()));
    }
    else if(currentFile.isDir()){
      toReturn.append(findMusicInDirWithMatcher(
            dir.absoluteFilePath(currentFile.absoluteFilePath()), fileMatcher));
    }
  }
  return toReturn;
}

QRegExp MusicFinder::getMusicFileMatcher(){
  QStringList availableTypes = availableMusicTypes();
  QString matcherString="";
  for(int i=0;i<availableTypes.size();++i){
    if(i==availableTypes.size()-1){
      matcherString += "(.*" + availableTypes.at(i) + ")";
    }
    else{
      matcherString += "(.*" + availableTypes.at(i) + ")|";
    }
  }
  DEBUG_MESSAGE("Matcher REGEX: " << matcherString.toStdString())
  QRegExp matcher(matcherString);
  return matcher;
}

QString MusicFinder::getMusicFileExtFilter(){
  QStringList availableTypes = availableMusicTypes();
  QString filterString="(";
  for(int i=0;i<availableTypes.size();++i){
    if(i==availableTypes.size()-1){
      filterString += "*." + availableTypes.at(i);
    }
    else{
      filterString += "*." + availableTypes.at(i) + " ";
    }
  }
  filterString += ")";
  DEBUG_MESSAGE("File Ext Filter: " << filterString.toStdString())
  return filterString;
}

QStringList MusicFinder::availableMusicTypes(){
  QStringList mimes = Phonon::BackendCapabilities::availableMimeTypes();
  for(int i=0; i< mimes.size(); ++i){
    DEBUG_MESSAGE("Mime: " << mimes.at(i).toStdString())
  }
  QStringList toReturn;
  if(mimes.contains("audio/flac") || mimes.contains("audio/x-flac")){
    toReturn.append("flac");
  }
  if(mimes.contains("audio/mp3") || mimes.contains("audio/x-mp3")){
    toReturn.append("mp3");
  }
  if(mimes.contains("audio/mp4")){
    toReturn.append("mp4");
  }
  if(mimes.contains("audio/m4a") 
    || ("audio/x-m4a") 
|| mimes.contains("applications/x-qt-m4a")){
    toReturn.append("m4a");
  }
  if(mimes.contains("audio/wav") || mimes.contains("audio/x-wav")){
    toReturn.append("wav");
  }
  if(mimes.contains("audio/ogg") ||
mimes.contains("application/ogg") ||
mimes.contains("audio/x-vorbis") || 
mimes.contains("audio/x-vorbis+ogg"))
{
    toReturn.append("ogg");
  }
  return toReturn;
}

} //end namespace
