# Remote boxes and long-running processes — gotchas

## A Pi-hole v6 command hangs forever

- **Symptom:** any `pihole …` call over ssh never returns and produces no output.
- **Means:** v6 prompts for the API password when it isn't run as root; the prompt waits on
  a tty that isn't there.
- **Fix:** `sudo pihole … </dev/null`, wrapped in a `timeout`. Both parts matter: the
  redirect kills the prompt, the timeout stops a hang from eating the session.

## `pkill -f` kills the wrong thing, and `pgrep -f` lies about it

- **Symptom:** a pattern match appears to find the process — or kills something unintended,
  including the session doing the checking.
- **Means:** `-f` matches the full command line, and the checking shell's own command line
  contains the pattern. The check matches itself.
- **Fix:** never `pkill -f` over ssh. Use the bracket trick (`pgrep -f "[h]ttp-server"`) so
  the pattern can't match its own process, and confirm a process is alive by the mtime of
  what it writes, not by a pattern hit.
