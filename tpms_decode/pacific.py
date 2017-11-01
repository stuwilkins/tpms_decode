# BSD 3-Clause License
#
# Copyright (c) 2017, Stuart Wilkins
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

import crcmod

_crc_prepend = '000000'
_crc_func = crcmod.mkCrcFun(0x113, rev=False, initCrc=0, xorOut=0)


def decode_pacific(payload):

    # Pad with zeros
    payload = '{0:0<66}'.format(payload[1:])
    out = dict()

    # Break apart strings
    crc_string = _crc_prepend + payload
    crc_payload = map(''.join, zip(*([iter(crc_string)]*8)))
    if len(crc_payload) < 8:
        raise RuntimeError('Invalid payload length (could not format CRC)')
    crc_payload = crc_payload[:8]
    crc_calc = _crc_func(''.join([chr(int(i, 2)) for i in crc_payload]))
    crc_val = int(payload[58:66], 2)
    if crc_calc != crc_val:
        raise RuntimeError('CRC Check Failed')

    press_check = int(payload[34:42], 2) ^ int(payload[42:50], 2)
    if press_check != 0xFF:
        raise RuntimeError('Pressure check failed')

    out['id'] = '{:02X}'.format(int(payload[0:28], 2))
    out['batt_ok'] = int(payload[28:29], 2) == 0
    out['counter'] = int(payload[29:31], 2)
    out['unk'] = '0x{:X}'.format(int(payload[31:34], 2))
    out['pressure'] = (int(payload[34:42], 2) - 40) * 0.363
    out['temp'] = (int(payload[50:58], 2) - 40)

    return out


if __name__ == "__main__":
    s = '110000001111100100000111001001110000111110110000010001100010011000111'
    import sys
    with open(sys.argv[1], 'r') as infile:
        for line in infile:
            ls = line.rstrip().split()
            if len(ls) == 6:
                try:
                    print(decode_pacific(ls[5]))
                except RuntimeError:
                    print('Unable to read {}'.format(ls[5]))
                    pass
