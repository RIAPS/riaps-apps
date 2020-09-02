//
// Created by istvan on 11/11/16.
//

#include "Receiver.h"
#include <capnp/serialize.h>
#include <capnp/message.h>

#define SAMPLING_RATE 1000 // Hz
#define SIGNAL_FREQ 60 // Hz
#define PWM_PERIOD 4000 // nanoseconds


#define SAMPLING_INTERVAL (1000000000L / SAMPLING_RATE) // nanoseconds
#define DPHASE (2 * M_PI * SIGNAL_FREQ / SAMPLING_RATE)

#define PWM_OUTPUT_CHIP 0
#define PWM_CHIP_OUTPUT 0

#define BILLION 1000000000l


namespace timertest {
    namespace components {

        Receiver::Receiver(const py::object *parent_actor,
                           const py::dict actor_spec, // Actor json config
                           const py::dict type_spec,  // component json config
                           const std::string &name,
                           const std::string &type_name,
                           const py::dict args,
                           const std::string &application_name,
                           const std::string &actor_name,
                           const py::list groups) : ReceiverBase(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                          application_name,
                                                                          actor_name,
                                                                          groups) {
            _pps_output = libsoc_gpio_request(PPS_OUTPUT, LS_GPIO_SHARED);
            if (!_pps_output) {
                perror("unable to request gpio pin:");
                exit(-1);
            }
            libsoc_gpio_set_direction(_pps_output, OUTPUT);
            sleep(1);
            if (libsoc_gpio_get_direction(_pps_output) != OUTPUT)
            {
                perror("unable to set output direction:");
                exit(-1);
            }
        }

        void Receiver::OnSignalValue() {
            auto [msg, error] = RecvSignalValue();
            auto currentValue     = msg->getVal();
            auto capnpTimestamp = msg->getTimestamp();
            auto tsCurrentTimestamp = timespec{capnpTimestamp.getSec(), capnpTimestamp.getNsec()};


            if (_lastValue<0 && currentValue>0){
                double alastval = fabs(asin(_lastValue));
                double acurrval = fabs(asin(currentValue));


                double m = alastval/(acurrval+alastval);

                timespec tsDiff;
                tsDiff.tv_sec = tsCurrentTimestamp.tv_sec - _lastTimestamp.tv_sec;
                tsDiff.tv_nsec = tsCurrentTimestamp.tv_nsec - _lastTimestamp.tv_nsec;

                if (tsDiff.tv_nsec<0){
                    tsDiff.tv_sec--;
                    tsDiff.tv_nsec+=BILLION;
                }
                int nsDiff = tsDiff.tv_sec*BILLION + tsDiff.tv_nsec;
                int tsOffset = m*nsDiff;
                timespec predTs;
                predTs.tv_nsec = _lastTimestamp.tv_nsec + tsOffset + 16666666+1836650; // RC filter phase shift at 60Hz
                predTs.tv_sec = _lastTimestamp.tv_sec;

                while (predTs.tv_nsec>BILLION){
                    predTs.tv_sec++;
                    predTs.tv_nsec-=BILLION;
                }

                clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &predTs, NULL);
                // if (_isHigh){
                //     _isHigh = false;
                //     libsoc_gpio_set_level(_pps_output, LOW);
                // } else {
                //     _isHigh = true;
                //     libsoc_gpio_set_level(_pps_output, HIGH);
                // }
                libsoc_gpio_set_level(_pps_output, HIGH);
                libsoc_gpio_set_level(_pps_output, LOW);


            }
            _lastValue = currentValue;
            _lastTimestamp = tsCurrentTimestamp;
        }

//        void Receiver::OnOneShotTimer(const std::string &timerid) {
//
//            libsoc_gpio_set_level(_pps_output, HIGH);
//            libsoc_gpio_set_level(_pps_output, LOW);
//
//        }

        Receiver::~Receiver() {
            libsoc_gpio_free(_pps_output);
        }
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
                    const py::list groups) {
    auto ptr = new timertest::components::Receiver(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                    application_name,
                                                    actor_name,
                                                    groups);
    return std::move(std::unique_ptr<timertest::components::Receiver>(ptr));
}

PYBIND11_MODULE(libreceiver, m) {
    py::class_<timertest::components::Receiver> testClass(m, "Receiver");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&, const py::list>());

    testClass.def("setup"                 , &timertest::components::Receiver::Setup);
    testClass.def("activate"              , &timertest::components::Receiver::Activate);
    testClass.def("terminate"             , &timertest::components::Receiver::Terminate);
    testClass.def("handlePortUpdate"      , &timertest::components::Receiver::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &timertest::components::Receiver::HandleCPULimit);
    testClass.def("handleMemLimit"        , &timertest::components::Receiver::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &timertest::components::Receiver::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &timertest::components::Receiver::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &timertest::components::Receiver::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &timertest::components::Receiver::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &timertest::components::Receiver::HandleReinstate);
    testClass.def("handleActivate"        , &timertest::components::Receiver::HandleActivate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
