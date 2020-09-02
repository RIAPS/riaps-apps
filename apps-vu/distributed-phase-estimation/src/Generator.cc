//
// Created by istvan on 11/11/16.
//

#include "Generator.h"
#include <capnp/serialize.h>
#include <capnp/message.h>

#define SAMPLING_RATE 1000 // Hz
#define SIGNAL_FREQ 60 // Hz
#define PWM_PERIOD 4000 // nanoseconds

#define DPHASE (2 * M_PI * SIGNAL_FREQ / SAMPLING_RATE)

#define PWM_OUTPUT_CHIP 0
#define PWM_CHIP_OUTPUT 0

namespace timertest{
    namespace components {

        Generator::Generator(const py::object *parent_actor,
                             const py::dict actor_spec, // Actor json config
                             const py::dict type_spec,  // component json config
                             const std::string &name,
                             const std::string &type_name,
                             const py::dict args,
                             const std::string &application_name,
                             const std::string &actor_name,
                             const py::list groups) : GeneratorBase(parent_actor, actor_spec, type_spec, name, type_name, args, application_name,
                                                                                 actor_name, groups) {

            int policy = SCHED_RR;
            struct sched_param params;
            params.sched_priority = 98;

            int prior_pol = sched_setscheduler(0,policy,&params);
            if (prior_pol == -1){
              std::cout << "SETSCHEDULER ERROR" << std::endl;

              int errsv = errno;
              if(errsv == EINVAL) std::cout << "EINVAL" << std::endl;
              if(errsv == EPERM) std::cout << "EPERM" << std::endl;
              if(errsv == ESRCH) std::cout << "ESRCH" << std::endl;
            }


            _pwm_output = libsoc_pwm_request(PWM_OUTPUT_CHIP, PWM_CHIP_OUTPUT, LS_PWM_SHARED);
            if (!_pwm_output) {
                perror("unable to request PWM pin:");
                fprintf(stderr, "make sure, you enabled the PWM overlay:\n\techo BB-PWM1 >  /sys/devices/platform/bone_capemgr/slots\n");
                exit(-1);
            }

            libsoc_pwm_set_enabled(_pwm_output, ENABLED);
            sleep(1);
            if (!libsoc_pwm_get_enabled(_pwm_output))
            {
                perror("unable to enable PWM pin:");
                exit(-1);
            }


            libsoc_pwm_set_polarity(_pwm_output, NORMAL);
            if (libsoc_pwm_get_polarity(_pwm_output) != NORMAL)
            {
                perror("unable to set PWM polarity:");
                exit(-1);
            }

            libsoc_pwm_set_period(_pwm_output, PWM_PERIOD);
            if (libsoc_pwm_get_period(_pwm_output) != PWM_PERIOD)
            {
                perror("unable to set PWM period:");
                exit(-1);
            }
        }

        // With RIAPS timer
        void Generator::OnClock() {
            auto msg = RecvClock();
            float currentValue = sin(_phase);
            _phase+=DPHASE;

            //capnp::MallocMessageBuilder messageBuilder;
            MessageBuilder<messages::SignalValue> msg_signal_value;
            msg_signal_value->setVal(currentValue);
            auto msg_timestamp   = msg_signal_value->initTimestamp();

            timespec
                      t1Spec
                    //, t2Spec
                    //, tAvg
                    ;

            libsoc_pwm_set_duty_cycle(_pwm_output, PWM_PERIOD * (1.0 + currentValue) / 2.0 );
            clock_gettime(CLOCK_REALTIME, &t1Spec);
            //clock_gettime(CLOCK_REALTIME, &t2Spec);
            //tAvg.tv_nsec = (t1Spec.tv_nsec + t2Spec.tv_nsec)/2.0;
            //tAvg.tv_sec  = (t1Spec.tv_sec  + t2Spec.tv_sec)/2.0;

            //msgTimeStamp.setNsec(tAvg.tv_nsec);
            //msgTimeStamp.setSec(tAvg.tv_sec);
            msg_timestamp.setNsec(t1Spec.tv_nsec);
            msg_timestamp.setSec(t1Spec.tv_sec);

            SendSignalValue(msg_signal_value);

        }

// --> Without RIAPS timer <--
//        void Generator::OnClock(riaps::ports::PortBase *port) {
//            auto now = std::chrono::high_resolution_clock::now();
//            _cycle=0;
//            while (true) {
//                float currentValue = sin(_phase);
//                _phase += DPHASE;
//                capnp::MallocMessageBuilder messageBuilder;
//                auto msgSignalValue = messageBuilder.initRoot<messages::SignalValue>();
//                auto msgTimeStamp = msgSignalValue.initTimestamp();
//                timespec
//                        t1Spec
//                //, t2Spec
//                //, tAvg
//                ;
//
//
//                auto diff = std::chrono::milliseconds(1);
//                now+=diff;
//
//                std::this_thread::sleep_until(now);
//
//
//
//
//                msgSignalValue.setVal(currentValue);
//
//
//
//
//                libsoc_pwm_set_duty_cycle(_pwm_output, PWM_PERIOD * (1.0 + currentValue) / 2.0);
//                clock_gettime(CLOCK_REALTIME, &t1Spec);
//                //clock_gettime(CLOCK_REALTIME, &t2Spec);
//                //tAvg.tv_nsec = (t1Spec.tv_nsec + t2Spec.tv_nsec)/2.0;
//                //tAvg.tv_sec  = (t1Spec.tv_sec  + t2Spec.tv_sec)/2.0;
//
//                //msgTimeStamp.setNsec(tAvg.tv_nsec);
//                //msgTimeStamp.setSec(tAvg.tv_sec);
//                msgTimeStamp.setNsec(t1Spec.tv_nsec);
//                msgTimeStamp.setSec(t1Spec.tv_sec);
//
//                SendSignalValue(messageBuilder, msgSignalValue);
//
//                if (++_cycle == 9000){
//                    break;
//                }
//            }
//        }

        Generator::~Generator() {
            libsoc_pwm_free(_pwm_output);
        }
    }
}

std::unique_ptr<timertest::components::Generator>
create_component_py(const py::object *parent_actor,
                    const py::dict actor_spec,
                    const py::dict type_spec,
                    const std::string &name,
                    const std::string &type_name,
                    const py::dict args,
                    const std::string &application_name,
                    const std::string &actor_name,
                    const py::list groups) {
    auto ptr = new timertest::components::Generator(parent_actor, actor_spec, type_spec, name, type_name, args,
                                                                    application_name,
                                                                    actor_name,
                                                                    groups);
    return std::move(std::unique_ptr<timertest::components::Generator>(ptr));
}

PYBIND11_MODULE(libgenerator, m) {
    py::class_<timertest::components::Generator> testClass(m, "Generator");
    testClass.def(py::init<const py::object*, const py::dict, const py::dict, const std::string&, const std::string&, const py::dict, const std::string&, const std::string&, const py::list>());

    testClass.def("setup"                 , &timertest::components::Generator::Setup);
    testClass.def("activate"              , &timertest::components::Generator::Activate);
    testClass.def("terminate"             , &timertest::components::Generator::Terminate);
    testClass.def("handlePortUpdate"      , &timertest::components::Generator::HandlePortUpdate);
    testClass.def("handleCPULimit"        , &timertest::components::Generator::HandleCPULimit);
    testClass.def("handleMemLimit"        , &timertest::components::Generator::HandleMemLimit);
    testClass.def("handleSpcLimit"        , &timertest::components::Generator::HandleSpcLimit);
    testClass.def("handleNetLimit"        , &timertest::components::Generator::HandleNetLimit);
    testClass.def("handleNICStateChange"  , &timertest::components::Generator::HandleNICStateChange);
    testClass.def("handlePeerStateChange" , &timertest::components::Generator::HandlePeerStateChange);
    testClass.def("handleReinstate"       , &timertest::components::Generator::HandleReinstate);
    testClass.def("handleActivate"        , &timertest::components::Generator::HandleActivate);

    m.def("create_component_py", &create_component_py, "Instantiates the component from python configuration");
}
