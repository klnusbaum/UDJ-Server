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
#ifndef SETTINGS_WIDGET_HPP
#define SETTINGS_WIDGET_HPP
#include <QWidget>

class QCheckBox;

namespace UDJ{

/**
 * \brief Widget used to view and adjust UDJ settings
 */
class SettingsWidget : public QWidget{
Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /**
   * \brief Constructs a SettingsWidget
   *
   * @param parent The parent widget.
   */
  SettingsWidget(QWidget* parent=0);

  //@}

private:
  /** @name Private Members */
  //@{

  /** 
   * \brief Checkbox indicating whether or not file uploads should be allowed.
   */
  QCheckBox* allowFileUploads;

  //@}

  /** @name Private Functions */
  //@{

  /** \brief Sets up all the UI components that make up the widget. */
  void setupUi();

  //@}
};


} //end namespace
#endif //SETTINGS_WIDGET_HPP
