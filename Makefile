
# builds the packed script
packed.py: ./src/__main__.py
	python3 pack.py > packed.py



# test binaries
./tests/recursion: ./tests/recursion.c
	gcc -O0 -o ./tests/recursion ./tests/recursion.c

./tests/ro_mem: ./tests/ro_mem.c
	gcc -O0 -o ./tests/ro_mem ./tests/ro_mem.c

./tests/normal: ./tests/normal.c
	gcc -O0 -o ./tests/normal ./tests/normal.c

./tests/large_alloc: ./tests/large_alloc.c
	gcc -O0 -o ./tests/large_alloc ./tests/large_alloc.c


build: ./tests/normal ./tests/recursion ./tests/ro_mem ./tests/large_alloc

# all the test instances
test_normal: packed.py build
	python3 packed.py ./tests/testcases ./tests/normal

test_recursion: packed.py build
	python3 packed.py ./tests/testcases ./tests/recursion

test_romem: packed.py build
	python3 packed.py ./tests/testcases ./tests/ro_mem

test_large_alloc: packed.py build
	python3 packed.py ./tests/testcases ./tests/large_alloc

# invokes all the tests
test: test_romem test_recursion test_normal test_large_alloc

# clean it up
clean:
	-rm ./tests/recusion
	-rm ./tests/ro_mem
	-rm ./tests/recursion
	-rm ./tests/normal
	-rm ./tests/large_alloc
	-rm ./packed.py
