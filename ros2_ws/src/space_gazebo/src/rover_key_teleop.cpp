// Copyright 2026
// SPDX-License-Identifier: MIT

#include "space_gazebo/rover_key_teleop.hpp"

#include <QCoreApplication>
#include <QEvent>
#include <QKeyEvent>
#include <QTimer>
#include <Qt>
#include <gz/msgs/twist.pb.h>

#include <algorithm>

#include <gz/plugin/Register.hh>

namespace space_gazebo
{

RoverKeyTeleop::RoverKeyTeleop()
{
  this->title = "Rover keyboard control";
  this->command_publisher_ =
    this->node_.Advertise<gz::msgs::Twist>("/cmd_vel_in");

  this->publish_timer_ = new QTimer(this);
  QObject::connect(
    this->publish_timer_, &QTimer::timeout,
    this, [this]() {this->publishCommand();});

  if (QCoreApplication::instance() != nullptr) {
    QCoreApplication::instance()->installEventFilter(this);
  }
}

RoverKeyTeleop::~RoverKeyTeleop()
{
  if (QCoreApplication::instance() != nullptr) {
    QCoreApplication::instance()->removeEventFilter(this);
  }
}

void RoverKeyTeleop::LoadConfig(
  const tinyxml2::XMLElement * plugin_element)
{
  if (plugin_element != nullptr) {
    plugin_element->QueryDoubleAttribute(
      "forward_speed", &this->forward_speed_);
    plugin_element->QueryDoubleAttribute(
      "reverse_speed", &this->reverse_speed_);
    plugin_element->QueryDoubleAttribute(
      "turn_speed", &this->turn_speed_);

    double publish_rate_hz = 20.0;
    plugin_element->QueryDoubleAttribute(
      "publish_rate_hz", &publish_rate_hz);
    if (publish_rate_hz > 0.0) {
      this->publish_period_ms_ = std::max(
        1, static_cast<int>(1000.0 / publish_rate_hz));
    }
  }

  this->publish_timer_->start(this->publish_period_ms_);
}

bool RoverKeyTeleop::eventFilter(QObject * watched, QEvent * event)
{
  (void)watched;

  if (
    event->type() == QEvent::ApplicationDeactivate ||
    event->type() == QEvent::WindowDeactivate)
  {
    if (this->anyMotionKeyPressed()) {
      this->clearKeys();
      this->publishCommand(true);
    }
    return false;
  }

  if (
    event->type() != QEvent::KeyPress &&
    event->type() != QEvent::KeyRelease)
  {
    return false;
  }

  auto * key_event = static_cast<QKeyEvent *>(event);
  if (key_event->isAutoRepeat()) {
    return false;
  }

  const bool pressed = event->type() == QEvent::KeyPress;
  if (pressed && key_event->key() == Qt::Key_Space) {
    this->clearKeys();
    this->publishCommand(true);
    return false;
  }

  if (!this->setKeyState(key_event->key(), pressed)) {
    return false;
  }

  // Publish transitions immediately; the timer refreshes held commands so
  // the downstream command watchdog never expires during continuous input.
  this->publishCommand(true);
  return false;
}

bool RoverKeyTeleop::setKeyState(int key, bool pressed)
{
  switch (key) {
    case Qt::Key_Up:
      this->forward_pressed_ = pressed;
      return true;
    case Qt::Key_Down:
      this->reverse_pressed_ = pressed;
      return true;
    case Qt::Key_Left:
      this->left_pressed_ = pressed;
      return true;
    case Qt::Key_Right:
      this->right_pressed_ = pressed;
      return true;
    default:
      return false;
  }
}

bool RoverKeyTeleop::anyMotionKeyPressed() const
{
  return
    this->forward_pressed_ || this->reverse_pressed_ ||
    this->left_pressed_ || this->right_pressed_;
}

void RoverKeyTeleop::clearKeys()
{
  this->forward_pressed_ = false;
  this->reverse_pressed_ = false;
  this->left_pressed_ = false;
  this->right_pressed_ = false;
}

void RoverKeyTeleop::publishCommand(bool force)
{
  if (!force && !this->anyMotionKeyPressed()) {
    return;
  }

  gz::msgs::Twist command;

  if (this->forward_pressed_ != this->reverse_pressed_) {
    command.mutable_linear()->set_x(
      this->forward_pressed_ ? this->forward_speed_ : -this->reverse_speed_);
  }

  if (this->left_pressed_ != this->right_pressed_) {
    command.mutable_angular()->set_z(
      this->left_pressed_ ? this->turn_speed_ : -this->turn_speed_);
  }

  // A release transition forces one final zero command, but the idle timer
  // stays silent so it does not fight autonomous command sources.
  this->command_publisher_.Publish(command);
}

}  // namespace space_gazebo

GZ_ADD_PLUGIN(space_gazebo::RoverKeyTeleop, gz::gui::Plugin)
