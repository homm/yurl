from collections import deque


def _restore(cls, args):
    return tuple.__new__(cls, args)


def remove_dot_segments(path):
    stack = deque()
    last = 0
    for segment in path.split('/'):
        if segment == '.':
            pass
        elif segment == '..':
            if len(stack):
                stack.pop()
        else:
            stack.append(segment)
    if path.endswith(('/.', '/..')):
        stack.append('')
    return '/'.join(stack)
