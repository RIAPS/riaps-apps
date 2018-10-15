#include <Actuator.h>

namespace sltest {
   namespace components {
      
      Actuator::Actuator(_component_conf &config, riaps::Actor &actor) :
      ActuatorBase(config, actor) {
        //const char* hostname="127.0.0.1"; /* localhost */
        const char* hostname="10.76.0.144"; /* localhost */
        const char* portname="52000";

        memset(&hints,0,sizeof(hints));
        hints.ai_family=AF_UNSPEC;
        hints.ai_socktype=SOCK_DGRAM;
        hints.ai_protocol=0;
        hints.ai_flags=AI_ADDRCONFIG;
        int err=getaddrinfo(hostname,portname,&hints,&res);
        if (err!=0) {
            _logger->error("failed to resolve remote socket address (err={}, line:{})",err, __LINE__);
        } else {
          sockfd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
          if (sockfd==-1) {
              _logger->error("{} line: {}",strerror(errno), __LINE__);
          }
        }
        _logger->info("{} constructor finished", GetComponentName());
      }
      
      void Actuator::OnForce(const ForceType::Reader &message,
      riaps::ports::PortBase *port)
      {
          if (sockfd!=-1){
            double value = message.getValue();
            if (sendto(sockfd,&value,sizeof(value),0, res->ai_addr,res->ai_addrlen)==-1) {
              _logger->error("{} line:{}",strerror(errno), __LINE__);
            } else {

            }

        } else {
          _logger->error("Invalid sockfd");
        }
      }
      
      void Actuator::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      
      }
      
      Actuator::~Actuator() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new sltest::components::Actuator(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
