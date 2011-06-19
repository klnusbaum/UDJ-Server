#ifndef SETTINGS_WIDGET_HPP
#define SETTINGS_WIDGET_HPP
#include <QWidget>

class QCheckBox;

namespace UDJ{


class SettingsWidget : public QWidget{
Q_OBJECT
public:
  SettingsWidget(QWidget* parent=0);
private:
  void setupUi();
  QCheckBox* allowFileUploads;
};


} //end namespace
#endif //SETTINGS_WIDGET_HPP
