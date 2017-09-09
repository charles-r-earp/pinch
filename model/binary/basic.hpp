namespace pinch {
  namespace model {
    namespace binary {
      struct fixed {
        const float p;
        float operator()(const int bit) { return p; }
      }
    }
  }
}