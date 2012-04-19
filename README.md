## Instalation

Just clone this git repository and make urlfetcher.py symlink to your Google App Engine application directory.

## Regular usage

`urlfetcher.UrlFetcher` class it the tiny wrapper arounf native GAE urlfetch service with some more friendly API and capabilities to easing the test process.

### Sync calls

The basic usage is making syncronouse call to there remote resources:

    >>> from urlfetcher import UrlFetcher
    >>> fetcher = UrlFetcher(deadline=10)

    >>> response = fetcher.fetch('http://ya.ru/')
    >>> response
    <google.appengine.api.urlfetch._URLFetchResult object at ...>
    >>> response.status_code
    200

`fetch` method returns native GAE urlfetch response object with all its attibutes and properties.

### Async calls

`UrlFetcher` also suports asyncronous HTTP request with more simple API through so called _promises_. Then Promise object is called (or called its `wait` method) default handler just returns sucess response to there caller or raises exception if request has been failed:

    >>> promise = fetcher.fetch_async('http://ya.ru/')
    >>> promise
    <urlfetcher.Promise object at ...>
    >>> promise()
    <google.appengine.api.urlfetch._URLFetchResult object at ...>

Caller's code can specify custon success and/or error handlers:

    >>> def onsuccess(response):
    ...     print 'Status: %s' % response.satus_code

    >>> def onerror(e):
    ...     print 'Ups... there was error: %s' % e

    >>> promise(onsuccess)
    Status: 200

    >>> promise = fetcher.fetch_async('http://foo.bar/')
    >>> promise(onerror=onerror)
    Ups... there was error: DownloadError: ApplicationError: 2 [Errno -2] Name or service not known

## Stubbing (for tests)

For test purposes `UrlFetcher` instance can be replaced with `StubUrlFetcher` instance having same api but allows to provide precomputed responses for request.

`StubUrlFetcher` constructor accepts stab map as argument. Stub map is url (or regexp pattern) to response data mapping (dict). Response can be string, tuple of values (contenxt, status_code, headers, etc.), function that can receive request conxect or exception instance (that will be raise on corresponding url request):

    >>> fetcher = StubUrlFetcher({'http://ya.ru/': ('Hello World from Yandex!', 200)})

    >>> response = fetcher.fetch('http://ya.ru/')
    >>> response.status_code
    200
    >>> response.content
    Hello World from Yandex!

    >>> response = fetcher.fetch('http://ya.ru/')
    >>> response.status_code
    404

`StubUrlFetcher` also can fallback to real request if there is no required url in mapping:

    >>> fetcher = StubUrlFetcher({}, fallback=True)
    >>> response = fetcher.fetch('http://ya.ru/')
    >>> response.status_code
    200



