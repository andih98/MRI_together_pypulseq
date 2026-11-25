"""Create a copy of a .seq file that mimics a gradient hardware delay (for simulation only).

Gradients arriving `delay` seconds late relative to the ADC is the same as the ADC starting
`delay` seconds early, so every ADC event is moved forward by `delay`.
Simulate the copy (simulate.py does it) and reconstruct with the ORIGINAL .seq file.

usage: python tools/simulation/make_hw_delay_seq.py <in.seq> <out.seq> <delay_s>
"""

import sys

import pypulseq as pp

seq_in, seq_out, delay = sys.argv[1], sys.argv[2], float(sys.argv[3])

seq = pp.Sequence()
seq.read(seq_in)
n = 0
for i in seq.block_events:
    block = seq.get_block(i)
    if block.adc is not None:
        block.adc.delay -= delay
        assert block.adc.delay >= 0, f'block {i}: ADC delay would become negative'
        events = [e for e in (block.rf, block.gx, block.gy, block.gz, block.adc) if e is not None]
        events += list(getattr(block, 'label', {}).values()) if isinstance(getattr(block, 'label', None), dict) else []
        seq.set_block(i, *events)
        n += 1
seq.write(seq_out)
print(f'{n} ADCs shifted by {-delay * 1e6:.2f} us -> {seq_out}')
