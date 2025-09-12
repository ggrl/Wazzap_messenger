

USER_DB = {}
with open('users.dat', 'r') as f:
        for line in f:
            key, value = line.split(':')
            value = value.strip()
            USER_DB[key] = value

print(USER_DB['gregor'])