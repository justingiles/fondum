import copy
import collections

####################################################
#
#  COMMON UTILITIES USEFUL IN THE FONDUM CONTEXT
#
####################################################

# TBD: add a 'merge_fields' function that does do insertion into the dest object.


def copy_fields(src=None, dest=None):
    if src is None:
        return {}
    if dest is None:
        return {}
    src_handler, src_fields, src_alias_map = parse_fields(src)
    dest_handler, dest_fields, dest_alias_map = parse_fields(dest)
    for k, v in src_fields.iteritems():
        if k in dest_fields:
            set_field(k, v, dest, dest_fields, dest_handler)
        if k in dest_alias_map:
            set_field(dest_alias_map[k], v, dest, dest_fields, dest_handler)
    if dest_handler in ["list", "mongoengine", "object"]:
        return dest
    return dest_fields


def set_field(k, v, dest, dest_copy, dest_handler):
    if dest_handler in ["list"]:
        index = int(k)
        dest[index] = v
    elif dest_handler in ["mongoengine", "object"]:
        dest.__setitem__(k, v)
    else:  # else dest_handler is "dictionary" or behaving like a dictionary
        dest[k] = v
    dest_copy[str(k)] = v
    return


def parse_fields(src):
    src_type = str(type(src))
    src_parents = [str(base) for base in src.__class__.__bases__]
    src_handler = None
    fields = {}
    alias_field_map = {}
    #
    # pre-check typing
    #
    if src_type == "<type 'list'>":
        src_handler = "list"
    elif "<class 'flask_mongoengine.Document'>" in src_parents:
        src_handler = "mongoengine"
    elif "<class 'mongoengine.document.Document'>" in src_parents:
        src_handler = "mongoengine"
    elif "<class 'mongoengine.document.EmbeddedDocument'>" in src_parents:
        src_handler = "mongoengine"
    elif "mongoengine.base.metaclasses.TopLevelDocumentMetaclass" in src_type:
        src_handler = "mongoengine_class"
    elif "flask_restful.fields.Nested" in src_type:
        src_handler = "flask_restful_object"
    elif "<class 'page.PageForm'>" in src_parents:
        src_handler = "wtf"
    elif src_type == "<type 'dict'>":
        src_handler = "dictionary"
    else:
        src_handler = "object"
    #
    # parse
    #
    if src_handler == "list":
        for k, v in enumerate(src):
            fields[str(k)] = copy.deepcopy(v)
    elif src_handler == "mongoengine":
        for k, v in src._fields.iteritems():
            strk = str(k)
            fields[strk] = src.__getitem__(k)
            v_type = str(type(fields[strk]))
            if 'ObjectId' in v_type:
                fields[strk] = str(fields[strk])
    elif src_handler == "mongoengine_class":
        for k, v in src._fields.iteritems():
            fields[k] = v
    elif src_handler == "dictionary":
        for k, v in src.iteritems():
            v_type = str(type(v))
            if 'flask_restful.fields' in v_type:
                src_handler = "flask_restful_marshal"
                if hasattr(v, "attribute"):
                    # yes, this mapping is odd. restful marshal is expecting
                    # the original name, not the mapping
                    alias_field_map[v.attribute] = v.attribute
            fields[str(k)] = v
    elif src_handler == "flask_restful_object":
        for k, v in src.nested.iteritems():
            v_type = str(type(v))
            if 'flask_restful.fields' in v_type:
                src_handler = "flask_restful_marshal"
                if hasattr(v, "attribute"):
                    # yes, this mapping is odd. restful marshal is expecting
                    # the original name, not the mapping
                    alias_field_map[v.attribute] = v.attribute
            fields[str(k)] = v
    elif src_handler == "wtf":
        for k, v in src._fields.iteritems():
            fields[str(k)] = v
    else:
        for k, v in vars(src).iteritems():
            fields[str(k)] = v
    return src_handler, fields, alias_field_map


def convert_MongoEngineDoc_to_PageForm(doc, wtf):
    import page  # this is done inside the function to prevent a loop

    (src_handler, src_fields, alias_field_map) = parse_fields(doc)
    if src_handler == "mongoengine":
        raise(ImportError("Unable to do _import_fields on a mongoengine doc instance."))
    if src_handler != "mongoengine_class":
        raise(Exception("Unable to do _import_fields. Is this assgined a mongoengine document?"))
    for key in src_fields:
        if not key.startswith("_"):
            if key != "id":
                setattr(wtf, key, page.StringField(key))
    zak()  # next: insert ordering
    # https://stackoverflow.com/questions/5848252/wtforms-form-class-subclassing-and-field-ordering


# eof
