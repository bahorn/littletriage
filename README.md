# littletriage

The Little Triage Tool That Could.

## Details

Scripts GDB to run a few things I want, on a folder of testcases (usual fuzzer
results). Probably better tools, but this one is mine.

Aiming for this to have no none default dependencies in the main script
(beyond GDB) so I can quickly drop it in something like a docker container with
no extra work.

## Usage

First, create a working script with:
`python3 pack.py > working.py`


## License

MIT
