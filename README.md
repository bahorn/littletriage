# littletriage

The Little Triage Tool That Could.

## Details

Tool to generate "triage" reports on crashing testcases. So like things from
your fuzzer, etc.

## Dependencies

The only non-default dependency this uses is `rypc`, to communicate with a child
GDB instance.

## Usage

First, create a working script with:
`python3 pack.py > working.py`

Then with something like:
`python3 packed.py ./tests/testcases ./tests/large_alloc`

You can get a result like:

```json
{
  "crashes": [
    {
      "name": "empty",
      "path": "./tests/testcases/empty",
      "analysis": {
        "meta": {
          "path": "./tests/testcases/empty",
          "size": 0,
          "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
        "gdb": {
          "reason": "SIGSEGV",
          "backtrace": [
            {
              "address": "0x00005555555551b9",
              "function": "main",
              "registers": {
                "rax": "0x0000000000000000",
                "rcx": "0x00007ffff7eae826",
                "rdx": "0x0000000000000000",
                "rbx": "0x0000000000000000",
                "rsi": "0x000000003b9cd000",
                "rdi": "0x0000000000000000",
                "rsp": "0x00007fffffffd7f0",
                "rbp": "0x00007fffffffd800",
                "r8": "0x0000000000000000",
                "r9": "0x0000000000000000",
                "r10": "0x0000000000000022",
                "r11": "0x000055555557a000",
                "r12": "0x00005555555550a0",
                "r13": "0x0000000000000000",
                "r14": "0x0000000000000000",
                "r15": "0x0000000000000000"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## License

MIT
