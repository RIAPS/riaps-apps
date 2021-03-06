// Generated by Cap'n Proto compiler, DO NOT EDIT
// source: timertest.capnp

#ifndef CAPNP_INCLUDED_bf2613a11018ba1c_
#define CAPNP_INCLUDED_bf2613a11018ba1c_

#include <capnp/generated-header-support.h>

#if CAPNP_VERSION != 6001
#error "Version mismatch between generated code and library headers.  You must use the same version of the Cap'n Proto compiler and library."
#endif


namespace capnp {
namespace schemas {

CAPNP_DECLARE_SCHEMA(99254ce5e61770e4);
CAPNP_DECLARE_SCHEMA(8e53206e30d94af8);

}  // namespace schemas
}  // namespace capnp

namespace timertest {
namespace messages {

struct TimeStamp {
  TimeStamp() = delete;

  class Reader;
  class Builder;
  class Pipeline;

  struct _capnpPrivate {
    CAPNP_DECLARE_STRUCT_HEADER(99254ce5e61770e4, 1, 0)
    #if !CAPNP_LITE
    static constexpr ::capnp::_::RawBrandedSchema const* brand() { return &schema->defaultBrand; }
    #endif  // !CAPNP_LITE
  };
};

struct SignalValue {
  SignalValue() = delete;

  class Reader;
  class Builder;
  class Pipeline;

  struct _capnpPrivate {
    CAPNP_DECLARE_STRUCT_HEADER(8e53206e30d94af8, 1, 1)
    #if !CAPNP_LITE
    static constexpr ::capnp::_::RawBrandedSchema const* brand() { return &schema->defaultBrand; }
    #endif  // !CAPNP_LITE
  };
};

// =======================================================================================

class TimeStamp::Reader {
public:
  typedef TimeStamp Reads;

  Reader() = default;
  inline explicit Reader(::capnp::_::StructReader base): _reader(base) {}

  inline ::capnp::MessageSize totalSize() const {
    return _reader.totalSize().asPublic();
  }

#if !CAPNP_LITE
  inline ::kj::StringTree toString() const {
    return ::capnp::_::structString(_reader, *_capnpPrivate::brand());
  }
#endif  // !CAPNP_LITE

  inline  ::int32_t getSec() const;

  inline  ::int32_t getNsec() const;

private:
  ::capnp::_::StructReader _reader;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::_::PointerHelpers;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::List;
  friend class ::capnp::MessageBuilder;
  friend class ::capnp::Orphanage;
};

class TimeStamp::Builder {
public:
  typedef TimeStamp Builds;

  Builder() = delete;  // Deleted to discourage incorrect usage.
                       // You can explicitly initialize to nullptr instead.
  inline Builder(decltype(nullptr)) {}
  inline explicit Builder(::capnp::_::StructBuilder base): _builder(base) {}
  inline operator Reader() const { return Reader(_builder.asReader()); }
  inline Reader asReader() const { return *this; }

  inline ::capnp::MessageSize totalSize() const { return asReader().totalSize(); }
#if !CAPNP_LITE
  inline ::kj::StringTree toString() const { return asReader().toString(); }
#endif  // !CAPNP_LITE

  inline  ::int32_t getSec();
  inline void setSec( ::int32_t value);

  inline  ::int32_t getNsec();
  inline void setNsec( ::int32_t value);

private:
  ::capnp::_::StructBuilder _builder;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
  friend class ::capnp::Orphanage;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::_::PointerHelpers;
};

#if !CAPNP_LITE
class TimeStamp::Pipeline {
public:
  typedef TimeStamp Pipelines;

  inline Pipeline(decltype(nullptr)): _typeless(nullptr) {}
  inline explicit Pipeline(::capnp::AnyPointer::Pipeline&& typeless)
      : _typeless(kj::mv(typeless)) {}

private:
  ::capnp::AnyPointer::Pipeline _typeless;
  friend class ::capnp::PipelineHook;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
};
#endif  // !CAPNP_LITE

class SignalValue::Reader {
public:
  typedef SignalValue Reads;

  Reader() = default;
  inline explicit Reader(::capnp::_::StructReader base): _reader(base) {}

  inline ::capnp::MessageSize totalSize() const {
    return _reader.totalSize().asPublic();
  }

#if !CAPNP_LITE
  inline ::kj::StringTree toString() const {
    return ::capnp::_::structString(_reader, *_capnpPrivate::brand());
  }
#endif  // !CAPNP_LITE

  inline float getVal() const;

  inline bool hasTimestamp() const;
  inline  ::timertest::messages::TimeStamp::Reader getTimestamp() const;

private:
  ::capnp::_::StructReader _reader;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::_::PointerHelpers;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::List;
  friend class ::capnp::MessageBuilder;
  friend class ::capnp::Orphanage;
};

class SignalValue::Builder {
public:
  typedef SignalValue Builds;

  Builder() = delete;  // Deleted to discourage incorrect usage.
                       // You can explicitly initialize to nullptr instead.
  inline Builder(decltype(nullptr)) {}
  inline explicit Builder(::capnp::_::StructBuilder base): _builder(base) {}
  inline operator Reader() const { return Reader(_builder.asReader()); }
  inline Reader asReader() const { return *this; }

  inline ::capnp::MessageSize totalSize() const { return asReader().totalSize(); }
#if !CAPNP_LITE
  inline ::kj::StringTree toString() const { return asReader().toString(); }
#endif  // !CAPNP_LITE

  inline float getVal();
  inline void setVal(float value);

  inline bool hasTimestamp();
  inline  ::timertest::messages::TimeStamp::Builder getTimestamp();
  inline void setTimestamp( ::timertest::messages::TimeStamp::Reader value);
  inline  ::timertest::messages::TimeStamp::Builder initTimestamp();
  inline void adoptTimestamp(::capnp::Orphan< ::timertest::messages::TimeStamp>&& value);
  inline ::capnp::Orphan< ::timertest::messages::TimeStamp> disownTimestamp();

private:
  ::capnp::_::StructBuilder _builder;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
  friend class ::capnp::Orphanage;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::_::PointerHelpers;
};

#if !CAPNP_LITE
class SignalValue::Pipeline {
public:
  typedef SignalValue Pipelines;

  inline Pipeline(decltype(nullptr)): _typeless(nullptr) {}
  inline explicit Pipeline(::capnp::AnyPointer::Pipeline&& typeless)
      : _typeless(kj::mv(typeless)) {}

  inline  ::timertest::messages::TimeStamp::Pipeline getTimestamp();
private:
  ::capnp::AnyPointer::Pipeline _typeless;
  friend class ::capnp::PipelineHook;
  template <typename, ::capnp::Kind>
  friend struct ::capnp::ToDynamic_;
};
#endif  // !CAPNP_LITE

// =======================================================================================

inline  ::int32_t TimeStamp::Reader::getSec() const {
  return _reader.getDataField< ::int32_t>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS);
}

inline  ::int32_t TimeStamp::Builder::getSec() {
  return _builder.getDataField< ::int32_t>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS);
}
inline void TimeStamp::Builder::setSec( ::int32_t value) {
  _builder.setDataField< ::int32_t>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS, value);
}

inline  ::int32_t TimeStamp::Reader::getNsec() const {
  return _reader.getDataField< ::int32_t>(
      ::capnp::bounded<1>() * ::capnp::ELEMENTS);
}

inline  ::int32_t TimeStamp::Builder::getNsec() {
  return _builder.getDataField< ::int32_t>(
      ::capnp::bounded<1>() * ::capnp::ELEMENTS);
}
inline void TimeStamp::Builder::setNsec( ::int32_t value) {
  _builder.setDataField< ::int32_t>(
      ::capnp::bounded<1>() * ::capnp::ELEMENTS, value);
}

inline float SignalValue::Reader::getVal() const {
  return _reader.getDataField<float>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS);
}

inline float SignalValue::Builder::getVal() {
  return _builder.getDataField<float>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS);
}
inline void SignalValue::Builder::setVal(float value) {
  _builder.setDataField<float>(
      ::capnp::bounded<0>() * ::capnp::ELEMENTS, value);
}

inline bool SignalValue::Reader::hasTimestamp() const {
  return !_reader.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS).isNull();
}
inline bool SignalValue::Builder::hasTimestamp() {
  return !_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS).isNull();
}
inline  ::timertest::messages::TimeStamp::Reader SignalValue::Reader::getTimestamp() const {
  return ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::get(_reader.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS));
}
inline  ::timertest::messages::TimeStamp::Builder SignalValue::Builder::getTimestamp() {
  return ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::get(_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS));
}
#if !CAPNP_LITE
inline  ::timertest::messages::TimeStamp::Pipeline SignalValue::Pipeline::getTimestamp() {
  return  ::timertest::messages::TimeStamp::Pipeline(_typeless.getPointerField(0));
}
#endif  // !CAPNP_LITE
inline void SignalValue::Builder::setTimestamp( ::timertest::messages::TimeStamp::Reader value) {
  ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::set(_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS), value);
}
inline  ::timertest::messages::TimeStamp::Builder SignalValue::Builder::initTimestamp() {
  return ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::init(_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS));
}
inline void SignalValue::Builder::adoptTimestamp(
    ::capnp::Orphan< ::timertest::messages::TimeStamp>&& value) {
  ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::adopt(_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS), kj::mv(value));
}
inline ::capnp::Orphan< ::timertest::messages::TimeStamp> SignalValue::Builder::disownTimestamp() {
  return ::capnp::_::PointerHelpers< ::timertest::messages::TimeStamp>::disown(_builder.getPointerField(
      ::capnp::bounded<0>() * ::capnp::POINTERS));
}

}  // namespace
}  // namespace

#endif  // CAPNP_INCLUDED_bf2613a11018ba1c_
