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
#ifndef LOGIN_WIDGET_HPP
#define LOGIN_WIDGET_HPP

#include <QStackedWidget>

class QLabel;
class QLineEdit;
class QPushButton;

namespace UDJ{

class UDJServerConnection;

class LoginWidget : public QStackedWidget{
Q_OBJECT
public:
  LoginWidget();

private:
  QLabel *logo;
  QLineEdit *usernameBox;
  QLineEdit *passwordBox;
  QPushButton *loginButton;
  QWidget *loginDisplay;
  QLabel *loggingInLabel;
  UDJServerConnection *serverConnection;

  void setupUi();

  static const QString& getUsernameHint(){
    static const QString usernameHint(tr("Username"));
    return usernameHint;
  }

  static const QString& getPasswordHint(){
    static const QString passwordHint(tr("Password"));
    return passwordHint;
  }

private slots:
  void doLogin();
  void startMainGUI();
  void displayLoginFailedMessage(const QString errorMessage);
};


} //end namespace UDJ


#endif //LOGIN_WIDGET_HPP


