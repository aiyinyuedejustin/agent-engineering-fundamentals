/* Original compile-only checks of the analysis host's Linux x86-64 ABI.
 * This is not target code and must not be linked or executed. */
#define _GNU_SOURCE
#include <stddef.h>
#include <fcntl.h>
#include <errno.h>
#include <linux/openat2.h>
#include <sys/syscall.h>
#if !defined(__x86_64__) || defined(__ILP32__)
#error This evidence interpretation is specifically Linux x86-64 LP64.
#endif
_Static_assert(SYS_openat2 == 437, "openat2 syscall number");
_Static_assert(sizeof(struct open_how) == 24, "open_how size");
_Static_assert(offsetof(struct open_how, flags) == 0, "flags offset");
_Static_assert(offsetof(struct open_how, mode) == 8, "mode offset");
_Static_assert(offsetof(struct open_how, resolve) == 16, "resolve offset");
_Static_assert((RESOLVE_NO_MAGICLINKS|RESOLVE_NO_SYMLINKS|RESOLVE_BENEATH)==0xe, "resolve mask");
_Static_assert((0xe & RESOLVE_NO_XDEV)==0, "not a no-mount-crossing mask");
_Static_assert((O_PATH|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC)==0x2b0000, "directory flags");
_Static_assert((O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK)==0xa0800, "leaf added flags");
_Static_assert(O_CREAT==0x40, "mode gate bit");
_Static_assert(EAGAIN==11 && ENOSYS==38, "selected fallback errno values");
