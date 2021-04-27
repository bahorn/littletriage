#include <stdlib.h>
#include <unistd.h>

#define ALLOC_SIZE 1000000000

int main() {
    int i;
    char *mem;
    // 1 GB
    mem = malloc(ALLOC_SIZE);
    for (i = 0; i < ALLOC_SIZE; i++) {
        mem[i] = 1;
    }
    sleep(10);
    free(mem);
}
