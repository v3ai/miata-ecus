# Run from a Renode CPU hook (self = the CPU, miata_machine = its machine; extension methods such as GetMachine are
# not visible inside exec): reads the probes listed in sys.miata_probes from emulated memory and
# logs one "SAMPLE {json}" line with the virtual time. Set up by the generated .resc; see run_ecu.py.
import sys, struct, json
_m = miata_machine
_b = _m.SystemBus
_out = {'t': round(_m.LocalTimeSource.ElapsedVirtualTime.TotalSeconds, 6)}
def _rd(addr, size):
    return bytes(bytearray([_b.ReadByte(addr + i) for i in range(size)]))
_fmt = {'f32': '<f', 'f64': '<d', 'u8': '<B', 'u16': '<H', 'u32': '<I', 'i8': '<b', 'i16': '<h', 'i32': '<i'}
for _n, _p in sys.miata_probes.items():
    if _p['kind'] == 'ptrstr':
        _a = struct.unpack('<I', _rd(_p['addr'], 4))[0]
        _out[_n] = _rd(_a, 64).split(b'\0')[0].decode('latin-1') if _a else None
        continue
    if _p['kind'] == 'reg32':        # a peripheral register, read as one 32-bit access
        _out[_n] = int(_b.ReadDoubleWord(_p['addr']))
        continue
    if _p['kind'] == 'bytes':
        _raw = _rd(_p['addr'], min(_p['size'], 64))
        _out[_n] = _raw.split(b'\0')[0].decode('latin-1')
    else:
        _v = struct.unpack(_fmt[_p['kind']], _rd(_p['addr'], _p['size']))[0] * _p['scale']
        _out[_n] = round(_v, 4) if isinstance(_v, float) else _v
# sensors through rusEFI's registry: entry = 12 bytes {useMock, valid, ..., mockValue, Sensor*}; StoredValueSensor
# keeps {bool Valid; float Value} at +8
for _n, _t in sys.miata_sensors.items():
    _e = sys.miata_registry + 12 * _t
    _ptr = struct.unpack('<I', _rd(_e + 8, 4))[0]
    if _ptr == 0:
        _out[_n] = None
        continue
    _valid = _b.ReadByte(_ptr + 8)
    _out[_n] = round(struct.unpack('<f', _rd(_ptr + 12, 4))[0], 3) if _valid else None
miata_log('SAMPLE ' + json.dumps(_out))
if getattr(sys, 'miata_debug_sensors', False):
    import binascii
    _e = sys.miata_registry + 12 * 1
    _ptr = struct.unpack('<I', _rd(_e + 8, 4))[0]
    miata_log('SENSORDBG entry=%s ptr=0x%x obj=%s' % (binascii.hexlify(_rd(_e, 12)), _ptr, binascii.hexlify(_rd(_ptr, 32)) if _ptr else ''))
