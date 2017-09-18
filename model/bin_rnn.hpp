#include "bin_rnn.netdef"
#include <caffe2/core/workspace.h>
#include <google/protobuf/message.h>
#include <istream>
#include <ostream>

namespace pinch {
  namespace model {
    class bin_rnn {
      private:
        using Tensor = caffe2::Tensor<caffe2::CPUContext>;
        caffe2::Workspace pred_ws;
        caffe2::NetBase *pred_init_net = 0, *pred_net = 0;
        float *pred_data = 0, *pred_tanh = 0;
      public:
        bin_rnn() {
          caffe2::NetDef net;
          net.ParseFromString(bin_rnn_netdef::pred_init_net);
          pred_init_net = pred_ws.CreateNet(net);
          assert(pred_init_net);
        }
        void read(std::istream& is) {
          
        }
        void write(std::ostream& os) {
            
        }
        float operator()(int bit) {
          return 0.5;
          std::cout << "bin_rnn operator()" << std::endl;
          if(bit == -1) {
            std::cout << "bin_rnn operator() bit == -1" << std::endl;
            //pred_init_net->Run();
            std::cout << "pred_init_net: " << pred_init_net << std::endl;
            if(!pred_net) {
              std::cout << "bin_rnn !pred_net" << std::endl;
              caffe2::NetDef net;
              net.ParseFromString(bin_rnn_netdef::pred_net);
              pred_net = pred_ws.CreateNet(net);
              assert(pred_net);
              pred_data = pred_ws.GetBlob("data")->GetMutable<Tensor>()->mutable_data<float>();
              assert(pred_data);
              pred_tanh = pred_ws.GetBlob("tanh")->GetMutable<Tensor>()->mutable_data<float>();
              assert(pred_tanh);
            }
            return 0.5;
          }
          else {
            pred_data[0] = bit ? 1 : -1;
            pred_net->Run();
            return (pred_tanh[0] + 1) / 2.0f;
          }
        }
    };
  };
};