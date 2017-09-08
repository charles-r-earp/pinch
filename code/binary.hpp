#include "code.hpp"
#include <cassert>
#include <istream>
#include <ostream>

namespace pinch {
  namespace code {
    namespace binary {
      class coder {
      public:
        static const u32 pmax = 4095;
      protected:
        u32 x1 = 0, x2 = 0xffffffff;
      };
      class encoder : public coder {
      public:
        void encode(int y, std::ostream& out, u32 p) {
          const u32 xmid = x1 + ((x2-x1) >> 12) * p;
          assert(xmid >= x1 && xmid < x2);
          if (y)
            x2=xmid;
          else
            x1=xmid+1;
          while (((x1^x2)&0xff000000)==0) {
            out.put(x2>>24);
            x1<<=8;
            x2=(x2<<8)+255;
          }
        }
        void flush(std::ostream& out) {
          while (((x1^x2)&0xff000000)==0) {
            out.put(x2>>24);
            x1<<=8;
            x2=(x2<<8)+255;
          }
          out.put(x2>>24);
        }
      };
      class decoder : public coder {
        u32 x = -1;
      public:
        int decode(std::istream& in, u32 p) {
          if (x == -1) {
            x = 0;
            for (int i=0; i<4; ++i) {
              int c = 0;
              if (in)  c = in.get();
              x=(x<<8)+(c&0xff);
            }
          }    
          const u32 xmid = x1 + ((x2-x1) >> 12) * p;
          assert(xmid >= x1 && xmid < x2);
          int y=0;
          if (x<=xmid) {
            y=1;
            x2=xmid;
          }
          else
            x1=xmid+1;
          while (((x1^x2)&0xff000000)==0) {
            x1<<=8;
            x2=(x2<<8)+255;
            int c = 0;
            if (in) c = in.get();
            x=(x<<8)+c;
          }
          return y;
        }
      };
      void compress(std::istream& in, std::ostream& out, u32 p) {
          encoder e;
          int c = in.get();
          while (in) {
            e.encode(0, out, p);
            for (int i=7; i>=0; --i)
              e.encode((c>>i)&1, out, p);
            c = in.get();
          }
          e.encode(1, out, p); 
          e.flush(out);
      }
      void decompress(std::istream& in, std::ostream& out, u32 p) {
        decoder d;
        while(!d.decode(in, p)) {
          int c=1;
          while(c<256)
          c+=c+d.decode(in, p);
          out.put(c-256);
        }
      }
    };
  };
};

