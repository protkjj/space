// Copyright 2026
// SPDX-License-Identifier: MIT

#ifndef SPACE_GAZEBO__ROVER_KEY_TELEOP_HPP_
#define SPACE_GAZEBO__ROVER_KEY_TELEOP_HPP_

#include <QObject>

#include <gz/gui/Plugin.hh>
#include <gz/transport/Node.hh>

class QEvent;
class QTimer;

namespace space_gazebo
{

class RoverKeyTeleop : public gz::gui::Plugin
{
  Q_OBJECT

public:
  RoverKeyTeleop();
  ~RoverKeyTeleop() override;

protected:
  void LoadConfig(const tinyxml2::XMLElement * plugin_element) override;
  bool eventFilter(QObject * watched, QEvent * event) override;

private:
  bool setKeyState(int key, bool pressed);
  bool anyMotionKeyPressed() const;
  void clearKeys();
  void publishCommand(bool force = false);

  gz::transport::Node node_;
  gz::transport::Node::Publisher command_publisher_;
  QTimer * publish_timer_{nullptr};

  bool forward_pressed_{false};
  bool reverse_pressed_{false};
  bool left_pressed_{false};
  bool right_pressed_{false};

  double forward_speed_{0.25};
  double reverse_speed_{0.20};
  double turn_speed_{0.70};
  int publish_period_ms_{50};
};

}  // namespace space_gazebo

#endif  // SPACE_GAZEBO__ROVER_KEY_TELEOP_HPP_
