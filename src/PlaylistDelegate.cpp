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
#include "PlaylistDelegate.hpp"
#include <QSpinBox>
#include <QSqlRelationalTableModel>


namespace UDJ{


PlaylistDelegate::PlaylistDelegate(QObject* parent):
  QSqlRelationalDelegate(parent)
{}

QWidget* PlaylistDelegate::createEditor(
  QWidget* parent, 
  const QStyleOptionViewItem& /*option*/, 
  const QModelIndex& index) const
{
  if(index.column() != 6){
    return 0;
  }
  QSpinBox* editor = new QSpinBox(parent);
  editor->setMinimum(0);
  return editor; 
}

void PlaylistDelegate::setEditorData(
  QWidget* editor,
  const QModelIndex& index) const
{
  ((QSpinBox*)editor)->setValue(index.model()->data(index).toInt());
}

void setModelData(
  QWidget* editor,
  QAbstractItemModel* model,
  const QModelIndex& index)
{
  int data = ((QSpinBox*)editor)->value();
  ((QSqlRelationalTableModel*)model)->setData(index, data);
}


} //end namespace
