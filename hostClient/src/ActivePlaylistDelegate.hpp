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
#ifndef ACTIVE_PLAYLIST_DELEGATE_HPP
#define ACTIVE_PLAYLIST_DELEGATE_HPP

#include <QSqlRelationalDelegate>
#include "ConfigDefs.hpp"

namespace UDJ{

/**
 * \brief A delegate used by the the ActivePLaylistView to display items from a
 * ActivePlaylistModel.
 */
class ActivePlaylistDelegate : public QSqlRelationalDelegate{
Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /**
   * \brief Constructs a ActivePlaylistDelegate.
   * 
   * @param parent The parent object.
   */
  ActivePlaylistDelegate(QObject* parent=0);

  //@}

  /** @name Overriden from QItemDelegate */
  //@{
  
  /** * \brief .  */
  QWidget* createEditor(
    QWidget* parent, 
    const QStyleOptionViewItem& option, 
    const QModelIndex& index) const;

  /** * \brief .  */
  void setEditorData(
    QWidget* editor,
    const QModelIndex& index) const;

  /** * \brief .  */
  void setModelData(
    QWidget* editor,
    QAbstractItemModel* model,
    const QModelIndex& index);

  //@}
};


} //end namespace
#endif //ACTIVE_PLAYLIST_DELEGATE_HPP
