#include <queue>

namespace pinch {
  namespace model {
    namespace binary {
      class count_method {
        private:
          static const int buffer_size = 1 << 12;
          std::queue<int> bits;
          int count;
        public:
          float operator()(const int bit) {
            if (bit == -1) {
              count = 0;
              bits = std::queue<int>();
              return 0.5;
            }
            else {
              count += bit;
              bits.push(bit);
              if(bits.size() >= buffer_size) {
                count -= bits.front();
                bits.pop();
              }
              float p = float(count)/bits.size();
              return p;
            }
          }
      };
    };
  };
};