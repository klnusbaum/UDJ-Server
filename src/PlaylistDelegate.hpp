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
#ifndef PLAYLIST_DELEGATE_HPP
#define PLAYLIST_DELEGATE_HPP

#include <QSqlRelationalDelegate>

namespace UDJ{


class PlaylistDelegate : public QSqlRelationalDelegate{
Q_OBJECT
public:
  PlaylistDelegate(QObject* parent=0);
  QWidget* createEditor(
    QWidget* parent, 
    const QStyleOptionViewItem& option, 
    const QModelIndex& index) const;
  void setEditorData(
    QWidget* editor,
    const QModelIndex& index) const;
  void setModelData(
    QWidget* editor,
    QAbstractItemModel* model,
    const QModelIndex& index);
};


} //end namespace
#endif //PLAYLIST_DELEGATE_HPP
