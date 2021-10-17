#!/usr/bin/env python3

def test_example_bangle(capsys):
    from pygdk import Mill
    onefinity = Mill('onefinity.json')
    onefinity.material = 'Soft Wood'
    onefinity.tool = '1/4" Downcut'
    onefinity.helix(c_x=0, c_y=0, diameter=67, depth=21, z_step=10)
    onefinity.helix(c_x=0, c_y=0, diameter=77, depth=21, z_step=10, outside=True)

    [out,err] = capsys.readouterr()
    with open('tests/test_examples/test_bangle.nc') as known_good_output:
        assert out == known_good_output.read()
