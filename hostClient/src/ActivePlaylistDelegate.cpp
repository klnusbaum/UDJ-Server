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
#include "ActivePlaylistDelegate.hpp"
#include "DifferenceSpinner.hpp"
#include "ActivePlaylistModel.hpp"


namespace UDJ{


ActivePlaylistDelegate::ActivePlaylistDelegate(QObject* parent):
  QSqlRelationalDelegate(parent)
{}

QWidget* ActivePlaylistDelegate::createEditor(
  QWidget* parent, 
  const QStyleOptionViewItem& /*option*/, 
  const QModelIndex& index) const
{
  if(index.column() != 6){
    return 0;
  }
  DifferenceSpinner* editor = new DifferenceSpinner(parent);
  return editor; 
}

void ActivePlaylistDelegate::setEditorData(
  QWidget* editor,
  const QModelIndex& index) const
{
	DifferenceSpinner* castedEditor = (DifferenceSpinner*)editor;
  castedEditor->setValue(index.model()->data(index).toInt());
	castedEditor->saveCurrentValue();
}

void setModelData(
  QWidget* editor,
  QAbstractItemModel* model,
  const QModelIndex& index)
{
  int diff = ((DifferenceSpinner*)editor)->getCurrentValueSavedValueDiff();
  ((ActivePlaylistModel*)model)->updateVoteCount(index, diff);
}


} //end namespace
