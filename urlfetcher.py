import re
from urllib import urlencode

from google.appengine.api import urlfetch


class Promise(object):
    def __init__(self, rpc, context):
        self.rpc = rpc
        self.context = context

        self.onsuccess = None
        self.onerror = None

    def __call__(self, *args, **kwargs):
        return self.wait(*args, **kwargs)

    def wait(self, onsuccess=None, onerror=None):
        onsuccess = onsuccess or self.onsuccess
        onerror = onerror or self.onerror

        try:
            response = self._get_result()
            if onsuccess:
                return onsuccess(response)
            return response
        except urlfetch.DownloadError, e:
            if onerror:
                return onerror(e)
            else:
                raise

    def bind(self, onsuccess=None, onerror=None):
        self.onsuccess = onsuccess or self.onsuccess
        self.onerror = onerror or self.onerror

    def _get_result(self):
        return self.rpc.get_result()


class UrlFetcher(object):
    def __init__(self, **kwargs):
        self.params = kwargs

    def fetch_async(self, url, payload=None, method='GET', headers={},
                    allow_truncated=False, follow_redirects=True):
        return self._fetch(dict(url=url, payload=payload, method=method,
                                headers=headers, allow_truncated=allow_truncated,
                                follow_redirects=follow_redirects))

    def fetch(self, *args, **kwargs):
        promise = self.fetch_async(*args, **kwargs)

        return promise()

    def _fetch(self, context):
        rpc = urlfetch.create_rpc(**self.params)

        if isinstance(context['payload'], (dict, list, tuple)):
            context['payload'] = urlencode(context['payload'])

        urlfetch.make_fetch_call(rpc, **context)

        return Promise(rpc, context)


class StubResult(object):
    def __init__(self, content=None, status_code=200, headers={},
                 content_was_truncated=False, final_url=None):
        self.content = content
        self.status_code = status_code
        self.content_was_truncated = content_was_truncated

        self.headers = urlfetch._CaselessDict()
        self.headers.update(headers)

        self.final_url = final_url


class StubPromise(Promise):
    def __init__(self, stub, context):
        self.stub = stub
        self.context = context

        self.onsuccess = None
        self.onerror = None

    def _get_result(self):
        stub = self.stub

        if callable(stub):
            stub = stub(self.context)

        if isinstance(stub, Exception):
            raise stub
        elif isinstance(stub, basestring):
            return StubResult(stub)
        elif isinstance(stub, (tuple, list)):
            return StubResult(*stub)

        return stub


class StubUrlFetcher(UrlFetcher):
    def __init__(self, stub_map, fallback=False):
        self.stub_map = stub_map
        self.fallback = fallback

    def _fetch(self, context):
        url = context['url']

        for pattern, stub in self.stub_map.iteritems():
            if re.match(pattern, url):
                return StubPromise(stub, context)

        if self.fallback:
            return super(StubUrlFetcher, self)._fetch(context)

        raise KeyError(url)
