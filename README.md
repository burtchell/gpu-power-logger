# gpu-power-logger

A python script that runs a program and records the GPU power usage.

Currently, this is only intended as a utility to write an [Impact Framework](https://github.com/Green-Software-Foundation/if) manifest file that can be used with my [`gpu-carbon-estimator`](https://github.com/dukeofjukes/gpu-carbon-estimator) plugin to estimate carbon emissions. I may expand this to be more general in the future.

## To run

Ensure python dependencies are installed:

```
pip install pynvml pyyaml
```

Run the script:

```
./driver.py ./path/to/my-program my-arg1 my-arg2
```

By default, the output will be in `./gpu_power.yml`. This script will prepend the contents in `manifest_header.yml`, then write each power usage log as an IF "input".