def calc(w, z, s, m):
    # shipping cost. w=weight, z=zone(1..3), s=speed, m=member flag
    if z == 1:
        if s == "express":
            if w <= 1:
                c = 10
            elif w <= 5:
                c = 20
            else:
                c = 30
            if m == True:
                c = c - c * 0.1
            return c
        else:
            if w <= 1:
                c = 5
            elif w <= 5:
                c = 10
            else:
                c = 15
            if m == True:
                c = c - c * 0.1
            return c
    elif z == 2:
        if s == "express":
            if w <= 1:
                c = 16
            elif w <= 5:
                c = 32
            else:
                c = 48
            if m == True:
                c = c - c * 0.1
            return c
        else:
            if w <= 1:
                c = 8
            elif w <= 5:
                c = 16
            else:
                c = 24
            if m == True:
                c = c - c * 0.1
            return c
    else:
        if s == "express":
            if w <= 1:
                c = 24
            elif w <= 5:
                c = 48
            else:
                c = 72
            if m == True:
                c = c - c * 0.1
            return c
        else:
            if w <= 1:
                c = 12
            elif w <= 5:
                c = 24
            else:
                c = 36
            if m == True:
                c = c - c * 0.1
            return c
