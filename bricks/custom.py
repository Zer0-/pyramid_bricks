def customizable(name, bases, namespace):
    if 'custom_attributes' in namespace:
        custom_attributes = namespace['custom_attributes']
        del namespace['custom_attributes']
    else:
        custom_attributes = ()
    new_namespace = namespace.copy()
    def customnew(cls, name, **new_attributes):
        for custom_attr in custom_attributes:
            if not custom_attr in new_attributes:
                raise TypeError("{} requires named argument {}".format(
                    cls.__name__, custom_attr))
        for base in cls.__bases__ + (cls,):
            clsdict = base.__dict__.copy()
            if '__new__' in clsdict:
                del clsdict['__new__']
            namespace.update(clsdict)
        namespace.update(new_attributes)
        return type(name, bases, namespace)
    new_namespace['__new__'] = customnew
    return type(name, bases, new_namespace)
