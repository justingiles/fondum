####################################################
#
#  COMMON UTILITIES USEFUL IN THE FONDUM CONTEXT
#
####################################################


def copy_fields(src=None, dest=None):
    '''
    Copy the key/value fields of the 'src' object to the 'dest' object.

    If a key in src object is not in dest, then that particular key is
    skipped. It is NOT inserted into dest.

    Any key in dest not in src is left alone.

    If the key's value requires conversion, then an attempt will be made to convert
    it. If it is unable to convert, then that key is skipped.

    Nothing is returned as the src object is modified in place.
    '''
    if src is None:
        return
    if dest is None:
        return
    src_handler, src_fields = parse_fields(src)
    dest_handler, dest_fields = parse_fields(dest)
    for k, v in src_fields.iteritems():
        if k in dest_fields:
            if dest_handler in ["list"]:
                index = int(k)
                dest[index] = v
            elif dest_handler in ["mongoengine"]:
                dest.__setitem__(k, v)
            else:  # else dest_handler is "dictionary" or behaving like a dictionary
                dest_fields[k] = v
    return

# TBD: add a 'merge_fields' function that does do insertion into the dest object.

def parse_fields(src):
    src_type = type(src)
    src_parents = [str(base) for base in src.__class__.__bases__]
    src_handler = None
    fields = {}
    if src_type=="<type 'list'>":
        src_handler = "list"
        for k, v in enumerate(src):
            fields[str(k)] = copy.deepcopy(v)
    elif "<class 'flask_mongoengine.Document'>" in src_parents:   # mongoengine handler
        src_handler = "mongoengine"
        for k, v in src._fields.iteritems():
            fields[str(k)]=src.__getitem__(k)
    else:
        src_handler = "dictionary"
        for k, v in vars(src).iteritems():
            fields[str(k)]=v
    return src_handler, fields
