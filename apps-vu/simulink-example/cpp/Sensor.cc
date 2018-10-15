#include <Sensor.h>


namespace sltest {
   namespace components {
      
      Sensor::Sensor(_component_conf &config, riaps::Actor &actor) :
      SensorBase(config, actor) {
          SetDebugLevel(_logger, spdlog::level::level_enum::debug);

        const char* hostname="0.0.0.0"; /* wildcard */
        const char* portname="51000";
        memset(&hints,0,sizeof(hints));
        hints.ai_family=AF_UNSPEC;
        hints.ai_socktype=SOCK_DGRAM;
        hints.ai_protocol=0;
        hints.ai_flags=AI_PASSIVE|AI_ADDRCONFIG;
        int err=getaddrinfo(hostname,portname,&hints,&res);
        if (err!=0) {
            _logger->error("failed to resolve local socket address (err={}, line:{})",err, __LINE__);
        } else {
            socketfd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
            if (socketfd==-1) {
                _logger->error("{}, line: {}",strerror(errno), __LINE__);
            } else {
                if (bind(socketfd,res->ai_addr,res->ai_addrlen)==-1) {
                    _logger->error("{}, line: {}",strerror(errno), __LINE__);
                }
                /** Define socket timeout here
                 else {
                    // set timeout, 1sec
                    struct timeval tv;
                    tv.tv_sec = 1;
                    tv.tv_usec = 0;
                    if (setsockopt(socketfd, SOL_SOCKET, SO_RCVTIMEO,&tv,sizeof(tv)) < 0) {
                        _logger->error("Couldn't set timeout on socket");
                    }
                }
                **/
            }
        }
        _logger->debug("{} constructor finished", GetComponentName());
      }
      
      void Sensor::OnClock(riaps::ports::PortBase *port) {
        _logger->info("{}",__FUNCTION__);
        if (socketfd == -1) return;
        double buffer;
        struct sockaddr_storage src_addr;
        socklen_t src_addr_len=sizeof(src_addr);
        //_logger->debug("{}->{} is waiting for UDP package", __FUNCTION__, "recvfrom()");
        ssize_t count=recvfrom(socketfd,&buffer,sizeof(buffer),0,(struct sockaddr*)&src_addr,&src_addr_len);
        //_logger->debug("{}->{} UDP package arrived", __FUNCTION__, "recvfrom()");
        if (count==-1) {
            _logger->error("{}, line: {}",strerror(errno), __LINE__);
        } else {
            // UDPPAckage -> capnpMessage
            capnp::MallocMessageBuilder builder;
            auto msgPosition = builder.initRoot<PositionType>();
            msgPosition.setValue(buffer);
            SendPosition(builder, msgPosition);
        }
       
      }
      
      
      void Sensor::OnGroupMessage(const riaps::groups::GroupId& groupId,
      capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port){
         
      }
      
      Sensor::~Sensor() {
         
      }
   }
}

riaps::ComponentBase *create_component(_component_conf &config, riaps::Actor &actor) {
   auto result = new sltest::components::Sensor(config, actor);
   return result;
}

void destroy_component(riaps::ComponentBase *comp) {
   delete comp;
}
