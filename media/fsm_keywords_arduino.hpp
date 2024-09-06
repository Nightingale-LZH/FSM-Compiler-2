#ifndef ___FSM_KEYWORD_ARDUINO_HPP___
#define ___FSM_KEYWORD_ARDUINO_HPP___

#include "Arduino.h"

#ifndef FSM_PROCESSED

#define FSM void
#define FOR for
#define WHILE while
#define DO do
#define IF if
#define ELSE else

#define GLOBAL 

#define SKIP

#define END_SKIP

#define YIELD 
void WAIT(int milliseconds) { sleep(milliseconds); }
void WAIT_UNLESS(bool condition) {  }

#define BREAK break
#define CONTINUE continue
#define RETURN return

#endif  //  FSM_PROCESSED

// -------------------------------------------------- //
//                WAIT Wtatment Related               //
// -------------------------------------------------- //
#define __DECLARE_TIME_VARIABLE(fsm_name) unsigned long __fsm_wait_time_variable_ ## fsm_name = 0;
#define __REGISTER_CURRENT_TIME(fsm_name) __fsm_wait_time_variable_ ## fsm_name = millis();
#define __IS_TIME_PASSED(fsm_name, time_ms) (millis() > __fsm_wait_time_variable_ ## fsm_name + (time_ms))

// -------------------------------------------------- //
//                 FSM State Operation                //
// -------------------------------------------------- //
#define __FSM_META_VARIABLE_DECLARATION(fsm_name) unsigned int __fsm_current_state_ ## fsm_name = 0;
#define __CURRENT_STATE(fsm_name) (__fsm_current_state_ ## fsm_name)
#define __CHANGE_STATE(fsm_name, new_state)  __fsm_current_state_ ## fsm_name = new_state;

#define RESET_FSM(fsm_name) __fsm_current_state_ ## fsm_name = 0;
#define IS_FSM_ENDED(fsm_name) (__fsm_current_state_ ## fsm_name == 1)

// -------------------------------------------------- //
//               FSM Min Runtime Related              //
// -------------------------------------------------- //
#define __DECLARE_MIN_RUNTIME_ITER_TIME_VARIABLE(fsm_name) unsigned long __fsm_min_runtime_iter_time_ ## fsm_name = 0;
#define __REGISTER_MIN_RUNTIME_ITER_CURRENT_TIME(fsm_name) __fsm_min_runtime_iter_time_ ## fsm_name = millis();
#define ___MIN_RUNTIME_IS_TIME_PASSED(fsm_name, time_ms) (millis() > __fsm_min_runtime_iter_time_ ## fsm_name + (time_ms))

#endif  //  ___FSM_KEYWORD_ARDUINO_HPP___

