#include <QMainWindow>

class QTabWidget;
class QPushButton;

class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  MetaWindow();
private:
  QTabWidget *tabs;
  QPushButton *startPartyButton, *endPartyButton;
};
