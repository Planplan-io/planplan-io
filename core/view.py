import asyncio, logging
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse,HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.utils.decorators import classonlymethod
from django.utils.functional import classproperty

class ContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs |= self.extra_context
        return kwargs


class View:

    http_method_names = ["get","post","put","patch","delete","head","options","trace",]
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classproperty
    def view_is_async(cls):
        handlers = [
            getattr(cls, method)
            for method in cls.http_method_names
            if (method != "options" and hasattr(cls, method))
        ]
        if not handlers:
            return False
        is_async = asyncio.iscoroutinefunction(handlers[0])
        if not all(asyncio.iscoroutinefunction(h) == is_async for h in handlers[1:]):
            raise ImproperlyConfigured( f"{cls.__qualname__} HTTP handlers must either be all sync or all async.")
        return is_async

    @classonlymethod
    def as_view(cls, **initkwargs):
      
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(f"The method name {key} is not accepted as a keyword argument to {cls.__name__}().")
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view only accepts arguments that are already attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.setup(request, *args, **kwargs)
            if not hasattr(self, "request"):
                raise AttributeError(f"{cls.__name__} instance has no 'request' attribute. Did you override setup() and forget to call super()?")
            return self.dispatch(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__annotations__ = cls.dispatch.__annotations__
        view.__dict__.update(cls.dispatch.__dict__)
        if cls.view_is_async:
            view._is_coroutine = asyncio.coroutines._is_coroutine

        return view

    def setup(self, request, *args, **kwargs):
    
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, request.method.lower(), self.http_method_not_allowed) if request.method.lower() in self.http_method_names else self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        logging.getLogger("django.request").warning("Method Not Allowed (%s): %s",request.method,request.path,extra={"status_code": 405, "request": request},)
        response = HttpResponseNotAllowed(self._allowed_methods())

        if self.view_is_async:
            async def func():
                return response
            return func()
        else:
            return response

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response.headers["Allow"] = ", ".join(self._allowed_methods())

        if self.view_is_async:
            async def func():
                return response
            return func()
        else:
            return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class TemplateView(ContextMixin, View):
    template_name = None
    template_engine = None
    response_class = TemplateResponse
    content_type = None

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault("content_type", self.content_type)
        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )
    
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))