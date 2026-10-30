#!/usr/bin/env python3
import os, sys, subprocess, time, shutil, signal
import pexpect

os.environ.setdefault('PICO_HSM_CI_DEVICE_ID', 'pico-aio-ci')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'docker')
BIN = os.path.join(BUILD, 'pico_fido2')
HOME = '/tmp/pico-aio-repro-gpg'
LOG = '/tmp/pico-aio-repro-emu.log'


def run(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)


def kill_agents():
    subprocess.run(['gpgconf', '--homedir', HOME, '--kill', 'all'], capture_output=True)
    subprocess.run(['pkill', '-x', 'scdaemon'], capture_output=True)
    subprocess.run(['pkill', '-x', 'gpg-agent'], capture_output=True)


def start_pcscd():
    subprocess.run(['pkill', '-x', 'pcscd'], capture_output=True)
    time.sleep(1)
    subprocess.Popen(['/usr/sbin/pcscd'], stdout=open('/tmp/pico-aio-repro-pcscd.log','wb'), stderr=subprocess.STDOUT)
    time.sleep(1)


def start_emu():
    log = open(LOG, 'ab')
    p = subprocess.Popen([BIN], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(30):
        time.sleep(0.5)
        r = run(['opensc-tool', '-an'])
        if '3b:da:18' in r.stdout:
            return p
    return p


def stop(p):
    try:
        p.terminate(); p.wait(timeout=5)
    except Exception:
        try: p.kill()
        except Exception: pass


def keygen():
    env = os.environ.copy(); env['GNUPGHOME'] = HOME
    with open(os.path.join(HOME, 'gpg-agent.conf'), 'w') as f:
        f.write('pinentry-program /usr/bin/pinentry-tty\n')
    subprocess.run(['gpgconf', '--homedir', HOME, '--kill', 'gpg-agent'], capture_output=True)
    child = pexpect.spawn('gpg', ['--card-edit', '--expert'], env=env, encoding='utf-8', timeout=30, dimensions=(40, 120))
    child.logfile = sys.stdout
    try:
        child.expect(r'gpg(?:/card)?>\s*'); child.sendline('admin')
        child.expect(r'gpg(?:/card)?>\s*'); child.sendline('key-attr')
        for _ in range(3):
            child.expect(r'Your selection\? '); child.sendline('2')
            child.expect(r'Your selection\? '); child.sendline('1')
            idx = child.expect([r'Admin PIN', r'Changing card key attribute for:', r'gpg(?:/card)?>\s*'], timeout=30)
            if idx == 0:
                child.send('12345678'); child.send('\r')
                child.expect([r'Changing card key attribute for:', r'gpg(?:/card)?>\s*'], timeout=30)
        child.sendline('generate')
        for _ in range(40):
            idx = child.expect([r'Make off-card backup', r'Please unlock the card', r'Please enter the Admin PIN',
                                r'Key is valid for\?', r'Is this correct\?', r'Real name:', r'Email address:',
                                r'Comment:', r'Change \(N\)ame, \(C\)omment, \(E\)mail or \(O\)kay',
                                r'gpg(?:/card)?>\s*', r'Bad PIN', r'error', pexpect.TIMEOUT], timeout=60)
            if idx == 0: child.sendline('n')
            elif idx == 1: child.send('123456'); child.send('\r')
            elif idx == 2: child.send('12345678'); child.send('\r')
            elif idx == 3: child.sendline('0')
            elif idx == 4: child.sendline('y')
            elif idx == 5: child.sendline('Repro User')
            elif idx == 6: child.sendline('repro@example.com')
            elif idx == 7: child.sendline('test')
            elif idx == 8: child.sendline('O')
            elif idx == 9:
                child.sendline('quit'); child.expect(pexpect.EOF, timeout=15); return True
            elif idx in (10,11):
                return False
            else:
                return False
    except Exception as e:
        print('keygen exception:', type(e).__name__, e)
        try: child.close(force=True)
        except Exception: pass
        return False
    return False


def sign_after_restart():
    env = os.environ.copy(); env['GNUPGHOME'] = HOME
    status = run(['gpg', '--homedir', HOME, '--card-status'])
    print(status.stdout)
    print(status.stderr, file=sys.stderr)
    out = run(['gpg', '--homedir', HOME, '--list-keys', '--with-colons'])
    fpr = None
    for line in out.stdout.splitlines():
        if line.startswith('fpr:'):
            fpr = line.split(':')[9]; break
    if not fpr:
        print('no fingerprint'); return False
    with open('/tmp/pico-aio-repro-plain.txt', 'w') as f: f.write('repro\n')
    child = pexpect.spawn('gpg', ['--homedir', HOME, '--local-user', fpr, '--armor', '--detach-sign',
                                  '-o', '/tmp/pico-aio-repro.sig', '/tmp/pico-aio-repro-plain.txt'],
                          env=env, encoding='utf-8', timeout=30, dimensions=(40, 120))
    child.logfile = sys.stdout
    ok = False
    try:
        for _ in range(12):
            idx = child.expect([r'Please insert the card', r'Please unlock the card', r'PIN', r'Please confirm',
                                r'Really use this key', r'Overwrite\?', r'\[oc\]\?', r'Invalid selection',
                                r'gpg: Signature made', r'Bad PIN', r'error', pexpect.EOF, pexpect.TIMEOUT], timeout=30)
            if idx == 0: pass
            elif idx in (1,2): child.send('123456'); child.send('\r')
            elif idx in (3,4): child.sendline('y')
            elif idx == 5: child.sendline('y')
            elif idx == 6: child.sendline('o')
            elif idx == 7: pass
            elif idx == 8: ok = True; break
            elif idx in (9,10,11): break
            else: break
    except Exception as e:
        print('sign exception:', type(e).__name__, e)
        try: child.close(force=True)
        except Exception: pass
    if not ok:
        return False
    v = run(['gpg', '--homedir', HOME, '--verify', '/tmp/pico-aio-repro.sig', '/tmp/pico-aio-repro-plain.txt'])
    return v.returncode == 0


def main():
    if not os.path.isfile(BIN):
        print('missing', BIN); return 2
    shutil.rmtree(HOME, ignore_errors=True); os.makedirs(HOME, mode=0o700)
    try: os.remove(os.path.join(ROOT, 'memory.flash'))
    except FileNotFoundError: pass
    for p in ['/tmp/pico-aio-repro.sig', '/tmp/pico-aio-repro-plain.txt', LOG]:
        try: os.remove(p)
        except FileNotFoundError: pass
    start_pcscd()
    emu = start_emu()
    try:
        if not keygen():
            print('KEYGEN_FAIL'); return 2
    finally:
        kill_agents(); stop(emu)
    # Simulate power cycle: keep memory.flash, restart process.
    emu = start_emu()
    try:
        ok = sign_after_restart()
        print('SIGN_AFTER_RESTART', 'PASS' if ok else 'FAIL')
        return 0 if ok else 1
    finally:
        kill_agents(); stop(emu)

if __name__ == '__main__':
    sys.exit(main())
