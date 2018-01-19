import copy
import collections
import wtforms

####################################################
#
#  COMMON UTILITIES USEFUL IN THE FONDUM CONTEXT
#
####################################################

# TBD: add a 'merge_fields' function that does do insertion into the dest object.


def copy_fields(src=None, dest=None, debug=False):
    if src is None:
        return {}
    if dest is None:
        return {}
    src_handler, src_fields, src_alias_map = parse_fields(src)
    dest_handler, dest_fields, dest_alias_map = parse_fields(dest)
    for k, v in src_fields.iteritems():
        if k in dest_fields:
            set_field(k, v, dest, dest_fields, dest_handler, src_handler)
        if k in dest_alias_map:
            set_field(dest_alias_map[k], v, dest, dest_fields, dest_handler, src_handler)
    if debug: zak()
    if dest_handler in ["list", "mongoengine", "object"]:
        return dest
    return dest_fields


def set_field(k, v, dest, dest_copy, dest_handler, src_handler):
    if src_handler in ["wtf"]:
        if v.type == "RadioField":
            if v.data == u"None":
                v.data = None  # this is, I believe, some kind of WTForms bug
        v = v.data
    if dest_handler in ["list"]:
        index = int(k)
        dest[index] = v
    elif dest_handler in ["mongoengine", "object"]:
        dest.__setitem__(k, v)
    elif dest_handler in ["wtf"]:
        dest._fields[k].data = v
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


def handle_form_imports(wtf):
    ''' this is an odd function as WTForms are odd birds. In order to handle ordering of fields,
    they have a 'meta' function that moves class variables to another class variable list
    called '_unbound_fields' during class definition. this function must be called in __init__
    before the super __init__ is called. '''
    if not hasattr(wtf, '_import_fields'):
        return
    doc = wtf._import_fields
    (src_handler, src_fields, alias_field_map) = parse_fields(doc)
    if src_handler == "mongoengine":
        raise(ImportError("Unable to do _import_fields on a mongoengine doc instance."))
    if src_handler != "mongoengine_class":
        raise(Exception("Unable to do _import_fields. Is this assgined a mongoengine document?"))
    for key in src_fields:
        if not key.startswith("_"):
            if key != "id":
                if key not in dir(wtf):
                    field = mapfield_ME_to_Form(key, doc.__dict__[key])
                    wtf._unbound_fields.append((key, field))

#  LEGACY VERSION USED ON CLASS BEFORE INSTANCING
#
# def handle_form_imports(wtf):
#     if not hasattr(wtf, '_import_fields'):
#         return
#     doc = wtf._import_fields
#     (src_handler, src_fields, alias_field_map) = parse_fields(doc)
#     if src_handler == "mongoengine":
#         raise(ImportError("Unable to do _import_fields on a mongoengine doc instance."))
#     if src_handler != "mongoengine_class":
#         raise(Exception("Unable to do _import_fields. Is this assgined a mongoengine document?"))
#     for key in src_fields:
#         if not key.startswith("_"):
#             if key != "id":
#                 if key not in dir(wtf):
#                     field = mapfield_ME_to_Form(key, doc.__dict__[key])
#                     setattr(wtf, key, field)

def mapfield_ME_to_Form(key, entry):
    import page  # this is done inside the function to prevent a loop

    t = str(entry)
    if hasattr(entry, "label"):
        label = entry.label
    else:
        label = entry.db_field
    validators = []
    #
    # id field type
    #
    if "BooleanField" in t:
        r = page.BooleanField(label)
    elif "DateTimeField" in t:
        r = page.DateTimeField(label)
    elif "IntField" in t:
        r = page.IntegerField(label)
        validators.append(wtforms.validators.NumberRange())
    else:
        r = page.StringField(label)
    #
    # check for SelectField
    #
    if hasattr(entry, "textarea"):
        if entry.textarea:
            r = page.TextAreaField(label)
    if entry.choices:
        choices = [(key, key) for key in entry.choices]
        if hasattr(entry, 'radio') and entry.radio==True:
            r = page.RadioField(label, choices=choices)
        else:
            r = page.SelectField(label, choices=choices)
    #
    # generic options
    #
    if entry.default is not None:
        r.kwargs["default"] = entry.default
    if hasattr(entry, "description"):
        r.kwargs["description"] = entry.description
    if entry.required is True:
        validators.append(wtforms.validators.Required())
    else:
        #  note: required=False, which is the default; removes all form of validation
        validators = [wtforms.validators.Optional()]
    if hasattr(entry, "display_only"):
        r.kwargs["display_only"] = entry.display_only
    #
    # append validators (ONLY if validators in use)
    #
    if validators:
        r.kwargs["validators"] = validators
    return r

    #  NOT YET DONE (defaults to StringField)
    # if "BinaryField
    # if "ComplexDateTimeField
    # if "DecimalField
    # if "DictField
    # if "DynamicField
    # if "EmailField
    # if "EmbeddedDocumentField
    # if "EmbeddedDocumentListField
    # if "FileField
    # if "FloatField
    # if "GenericEmbeddedDocumentField
    # if "GenericReferenceField
    # if "GeoPointField
    # if "ImageField
    # if "ListField
    # if "MapField
    # if "ObjectIdField
    # if "ReferenceField
    # if "SequenceField
    # if "SortedListField
    # if "URLField
    # if "UUIDField
    # if "PointField
    # if "LineStringField
    # if "PolygonField
    # if "MultiPointField
    # if "MultiLineStringField
    # if "MultiPolygonField

# eof
