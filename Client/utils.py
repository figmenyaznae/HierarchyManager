wrapNone = lambda s: None if s=='' else str(s)
extractIcon = lambda obj: '' if obj is None else obj.icon
def ratingStr(rating):
        if rating is None: return 'Not available'
        s = ""
        for i in xrange(rating):
            s += "*"
        for i in xrange(rating,5):
            s += "-"
        return s