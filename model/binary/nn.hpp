#include <caffe2/core/workspace.h>
#include <google/protobuf/message.h>

namespace pinch {
  namespace model {
    namespace binary {
      class nn {
        private:
          using Tensor = caffe2::Tensor<caffe2::CPUContext>;
          static const int buffer_size = 256;
          caffe2::NetDef init_net, train_net, pred_net;
          caffe2::Workspace ws;
          caffe2::CPUContext context;
          std::shared_ptr<caffe2::Blob> data_blob, target_blob, softmax_blob;
          float p;
          int buffer_index;
          void load(caffe2::NetDef& net, std::string filename) {
            std::string proto_folder = "model/binary/proto/nn/";
            std::fstream fs(proto_folder+filename+".proto", std::fstream::in);
            assert(fs.is_open());
            std::stringstream ss;
            ss << fs.rdbuf();
            auto success = net.ParseFromString(ss.str());
            assert(success);
          }
        public: 
          nn() {
            load(init_net, "init_net");
            ws.CreateNet(init_net);
            ws.RunNet(init_net.name());
            load(train_net, "train_net");
            data_blob.reset(ws.CreateBlob("data"));
            data_blob->GetMutable<Tensor>()->Resize<std::vector<int>>({buffer_size, 2});
            target_blob.reset(ws.CreateBlob("target"));
            target_blob->GetMutable<Tensor>()->Resize<std::vector<int>>({buffer_size});
            ws.CreateNet(train_net);
            load(pred_net, "pred_net");
            ws.CreateNet(pred_net);
            softmax_blob.reset(ws.CreateBlob("softmax"));
          }
          float operator()(const int bit){
            if(bit == -1) {
              ws.RunNet(init_net.name());
              p = 0.5;
              buffer_index = 0;
            }
            else {
              assert(bit == 0 || bit == 1);
              auto data = data_blob->GetMutable<Tensor>()->mutable_data<float>();
              data[2*buffer_index] = !bit;
              data[2*buffer_index+1] = bit;
              auto target = target_blob->GetMutable<Tensor>()->mutable_data<int>();
              target[buffer_index] = bit;
              ++buffer_index;
              if(buffer_index >= buffer_size) {
                buffer_index = 0;
                for(int i=0; i < 8; ++i)
                    ws.RunNet(train_net.name());
                ws.RunNet(pred_net.name());
                auto softmax = softmax_blob->GetMutable<Tensor>()->mutable_data<float>();
                p = softmax[1];
                float m = 0.3;
                if(p > (1 - m))
                    p = (1 - m);
                else if (p < m)
                    p = m;
              }
            }
            return p;
          }
      };
    };
  };
};