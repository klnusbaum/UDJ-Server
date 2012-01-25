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

#include "LoginDialog.hpp"
#include "LoginWidget.hpp"
#include <QPushButton>
#include <QGridLayout>
#include <QApplication>


namespace UDJ{


LoginDialog::LoginDialog(QWidget *parent, Qt::WindowFlags f)
  :QDialog(parent, f)
{
  setupUi();
}

void LoginDialog::accept(){
  loginButton->hide();
  loginWidget->doLogin();
}

void LoginDialog::reject(){
  QDialog::reject();
  QApplication::quit();
}

void LoginDialog::closeDialog(){
  done(QDialog::Accepted);
}

void LoginDialog::setupUi(){
  loginWidget = new LoginWidget(this);
  loginButton = new QPushButton(tr("Login"), this);
  loginButton->setDefault(true);
  loginButton->setAutoDefault(true);

  connect(
    loginWidget, 
    SIGNAL(startedMainGUI()), 
    this, 
    SLOT(closeDialog()));

  connect(
    loginWidget,
    SIGNAL(loginFailed()),
    loginButton,
    SLOT(show()));

  connect(
    loginButton,
    SIGNAL(clicked()),
    this,
    SLOT(accept()));

  QGridLayout *layout = new QGridLayout;
  layout->addWidget(loginWidget, 0,0,3,3);
  layout->addWidget(loginButton, 3,1);
  setLayout(layout);
}



} //end namespace UDJ
