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
#ifndef UTILS_HPP
#define UTILS_HPP
#include <QSqlQueryModel>
#include <QTableView>
#include <QSqlRecord>
#include <set>
#include <vector>

namespace UDJ{


namespace Utils{


template<class T> std::vector<T> getSelectedIds(
  const QTableView* view,
  const QSqlQueryModel* model,
  const QString& colName)
{
  QModelIndexList selected = view->selectionModel()->selectedIndexes();
  std::vector<T> selectedIds;
  std::set<int> rows;
  for(
    QModelIndexList::const_iterator it = selected.begin();
    it != selected.end();
    ++it
  )
  {
    rows.insert(it->row()); 
  }
  for(
    std::set<int>::const_iterator it = rows.begin();
    it != rows.end();
    ++it
  )
  {
    QSqlRecord selectedRecord = model->record(*it);
    selectedIds.push_back(
      selectedRecord.value(colName).value<library_song_id_t>());
  }
  return selectedIds;
}


} //end namespace utils


} //end namespae  UDJ
#endif //UTILS_HPP
