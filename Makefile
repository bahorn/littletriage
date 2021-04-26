
# builds the packed script
packed.py:
	python3 pack.py > packed.py


# test binaries
./tests/recursion:
	gcc -o ./tests/recursion ./tests/recursion.c

./tests/ro_mem:
	gcc -o ./tests/ro_mem ./tests/ro_mem.c

./tests/normal:
	gcc -o ./tests/normal ./tests/normal.c


build: ./tests/normal ./tests/recusion ./tests/ro_mem

# all the test instances
test_normal: packed.py build
	python3 packed.py ./tests/normal ./tests/testcases

test_recusion: packed.py build
	python3 packed.py ./tests/recusion ./tests/testcases

test_romem: packed.py build
	python3 packed.py ./tests/ro_mem ./tests/testcases/


# invokes all the tests
test: test_romem test_recusion test_normal

# clean it up
clean:
	-rm ./tests/recusion
	-rm ./tests/ro_mem
	-rm ./tests/recusion
	-rm ./packed.py
