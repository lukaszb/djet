import types
from django.core.handlers.wsgi import WSGIRequest
from django import test as django_test
from django.http import HttpResponse
from django.views import generic
from djet import testcases


class MockMiddleware(object):
    def process_request(self, request):
        request.middleware_was_here = True


class RequestFactoryTest(django_test.TestCase):
    def setUp(self):
        self.factory = testcases.RequestFactory()

    def test_create_request_should_return_request(self):
        request = self.factory.get()

        self.assertIsInstance(request, WSGIRequest)

    def test_create_request_should_return_request_processes_by_middleware(self):
        request = self.factory.get(
            middleware_classes=[
                MockMiddleware,
            ]
        )

        self.assertTrue(request.middleware_was_here)

    def test_init_should_create_shortcuts(self):
        request = self.factory.get()

        self.assertEqual(request.method, 'GET')


class MockView(generic.View):
    def mock_method(self):
        self.mock_method_called = True


class KwargsMockView(generic.View):
    test = None

    def get(self, *args, **kwargs):
        return self.test


def mock_function_view(request):
    return HttpResponse(status=200)


class ViewTestCaseTest(testcases.ViewTestCase):
    view_class = MockView
    middleware_classes = [MockMiddleware]

    def test_init_should_create_view_method_when_view_class_provided(self):
        self.assertIsInstance(self.view, types.FunctionType)

    def test_init_should_create_factory_instance_with_middleware_classes(self):
        self.assertIsInstance(self.factory, testcases.RequestFactory)
        self.assertIn(MockMiddleware, self.factory.middleware_classes)

    def test_creating_view_object(self):
        view_object = self.view_class()

        view_object.mock_method()

        self.assertTrue(view_object.mock_method_called)

    def test_view_object_should_have_request_and_arguments(self):
        request = 'request'
        args = ('a', 'b')
        kwargs = {'c': 'c'}

        view_object = self.create_view_object(request, *args, **kwargs)

        self.assertEqual(view_object.request, 'request')
        self.assertEqual(view_object.args, args)
        self.assertEqual(view_object.kwargs, kwargs)


class KwargsViewTestCaseTest(testcases.ViewTestCase):
    view_class = KwargsMockView
    view_kwargs = {'test': 'test'}

    def test_view_should_have_kwargs_when_view_kwargs_specified(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertEqual(response, 'test')

    def test_view_object_should_have_kwargs_when_view_kwargs_specified(self):
        view_object = self.create_view_object()

        self.assertEqual(view_object.test, 'test')


class ViewTestCaseFunctionViewTest(testcases.ViewTestCase):
    view_function = mock_function_view

    def test_assert_response_when_function_view_used(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
