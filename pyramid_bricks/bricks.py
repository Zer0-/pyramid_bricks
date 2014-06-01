from webob import Request

class MissingConfiguration(Exception):
    pass

class Bricks:
    """Facilitates initialization of given components to provide
    simple dependency injection."""

    def __init__(self):
        self.components = {}

    def add(self, component_type):
        if component_type in self.components:
            return self.components[component_type]
        args = []
        if hasattr(component_type, 'requires_configured'):
            try:
                args += [self.components[requirement] for requirement
                         in component_type.requires_configured]
            except KeyError as e:
                raise MissingConfiguration("{} requires something that "
                    "provides {} to be configured".format(
                        component_type, e.args[0]))
        if hasattr(component_type, 'depends_on'):
            args += [self.add_component(comp_type) for
                    comp_type in component_type.depends_on]
        component = component_type(*args)
        if hasattr(component, 'provides'):
            for provision in component_type.provides:
                self.components[provision] = component
        self.components[component_type] = component
        return component

def create_app(main_component):
    bricks = Bricks()
    main = bricks.add(main_component)

    def wsgi_app(environ, start_response):
        request = Request(environ)
        response = main(request)
        return response(environ, start_response)

    return wsgi_app