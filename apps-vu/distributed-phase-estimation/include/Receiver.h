#ifndef RIAPS_FW_GENERATOR_H
#define RIAPS_FW_GENERATOR_H


#include <libsoc_debug.h>
#include <libsoc_gpio.h>
#define PPS_OUTPUT  22

#include "base/ReceiverBase.h"

#define DEBUG_SAMPLES 200

namespace timertest {
    namespace components {

        class Receiver : public ReceiverBase {

        public:

            Receiver(const py::object *parent_actor,
                     const py::dict actor_spec, // Actor json config
                     const py::dict type_spec,  // component json config
                     const std::string &name,
                     const std::string &type_name,
                     const py::dict args,
                     const std::string &application_name,
                     const std::string &actor_name,
                     const py::list groups);

            Receiver(const Receiver&) = delete;
            Receiver()                = delete;


            void OnSignalValue();

            //void OnOneShotTimer(const std::string &timerid);

            virtual ~Receiver();

        private:
            double   _lastValue = 0.0;
            timespec _lastTimestamp;
            gpio*    _pps_output;
            bool     _isHigh = false;


            //std::array<timespec, DEBUG_SAMPLES> _timestamp;
            //std::array<timespec, DEBUG_SAMPLES> _predicted;
            //std::array<timespec, DEBUG_SAMPLES> _triggered;
            //std::array<double, DEBUG_SAMPLES> _lastVal;
            //std::array<double, DEBUG_SAMPLES> _currVal;
            //int idx = 0;


        };
    }
}

std::unique_ptr<timertest::components::Receiver>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups);


#endif
