
# HowTo install the latest (unofficial) version of pyndl

## Interactive login

    ssh <USERID>@bluebear.bham.ac.uk
    module load slurm-interactive
    fisbatch_tmux --nodes 1 --ntasks 1 --time 01:00:00 --mem=32GB --qos=divjakd
>   # or `bbdefault`

## Start your Python environment

    conda activate <ENVIRONMENT_NAME>

## Git clone

    git clone https://github.com/quantling/pyndl.git
    cd pyndl
    git checkout masking2

## Setup

    python setup.py develop

# Start Python for testing

    python
>   # or `ipython`

    from pyndl import ndl

    weights = ndl.ndl(events='tests/resources/event_file_masking.tab.gz', alpha=1.0, betas=(0.01, 0.01), method="threading", cues_to_mask={'a', 'b'})

    weights2 = ndl.dict_ndl(events='tests/resources/event_file_masking.tab.gz', alphas=1.0, betas=(0.01, 0.01), cues_to_mask={'a', 'b'})

> etc etc

> **NOTE:** You need `python setup.py develop` each time, if you want to use
> this version, I think.
> 
> This version contains `cue_to_mask` parameter, which I specifically requested
> to avoid so-called *auto-cueing* (outcome becomes a cue for itself). If you
> set `cue_to_mask='all'`, then all cues will be *masked* or disabled to
> auto-cue...

