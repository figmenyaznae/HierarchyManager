wrapNone = lambda s: None if s=='' else str(s)

extractIcon = lambda obj: '' if obj is None else obj.icon

def getRaiting(file):
    if len(file.ratings)>0:
        return reduce(lambda s, obj: s + obj.value, file.ratings, 0) / len(file.ratings)
    else:
        return 0

def ratingStr(rating):
        if rating is None: return 'Not available'
        s = ""
        for i in xrange(rating):
            s += "*"
        for i in xrange(rating,5):
            s += "-"
        return s