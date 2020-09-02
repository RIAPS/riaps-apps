#ifndef RIAPS_FW_GENERATOR_H
#define RIAPS_FW_GENERATOR_H

#include <libsoc_pwm.h>
#include <libsoc_debug.h>

#include "base/GeneratorBase.h"

namespace timertest {
    namespace components {

        class Generator : public GeneratorBase {

        public:

            Generator(const py::object *parent_actor,
                      const py::dict actor_spec, // Actor json config
                      const py::dict type_spec,  // component json config
                      const std::string &name,
                      const std::string &type_name,
                      const py::dict args,
                      const std::string &application_name,
                      const std::string &actor_name,
                      const py::list groups);

            Generator(const Generator&) = delete;
            Generator()                      = delete;



            virtual void OnClock();

            virtual ~Generator();

        private:
            double    _phase = 0.0;
            pwm*      _pwm_output;
            uint64_t  _cycle = 0;
        };
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
                    const py::list groups);

#endif
