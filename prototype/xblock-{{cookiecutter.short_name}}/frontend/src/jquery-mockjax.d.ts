/// <reference types="jquery" />
/**
 * Type definitions for Mockjax.
 * Converted from the JSDoc `@module TypeDefinitions` file in
 * "jquery-mockjax". Further edited to remove redundant types,
 * and then given a default export that matches behavior.
 */

declare module "jquery-mockjax" {
  /* ================================================================== *
   * Unions and primitives
   * ================================================================== */

  /** Valid HTTP methods. */
  type HTTPMethod =
    | "GET"
    | "POST"
    | "PUT"
    | "DELETE"
    | "HEAD"
    | "OPTIONS"
    | "CONNECT"
    | "TRACE"
    | "PATCH";

  /** Valid XHR readyState. */
  type ReadyState = 0 | 1 | 2 | 3 | 4;

  /**
   * Valid Ajax callback method types.
   * @internal
   */
  type AjaxCallbackType = "Success" | "Error" | "Complete";

  /* ================================================================== *
   * Function types
   * ================================================================== */

  /**
   * A method called once an async operation is complete.
   * @internal
   */
  type AsyncComplete = (...args: any[]) => void;

  /**
   * A callback with jQuery ajax settings as its only parameter.
   * @internal
   */
  type CallbackWithRequestSettings = (requestSettings: JQueryAjaxSettings) => void;

  /** Request data matching function. */
  type DataMatcherFn = (requestData: RequestData) => boolean;

  /** The matcher for request data. */
  type DataMatcher = DataMatcherFn | string | { [key: string]: DataMatcher };

  /** Data in the ajax request settings. */
  type RequestData = { [key: string]: string | RequestData | any[] };

  /** A function to determine if an ajax call should be matched or not. */
  type DynamicMockHandler = (requestSettings: JQueryAjaxSettings) => MockHandler | null;

  /**
   * A Deferred method to send args given context.
   * @internal
   */
  type MethodWithContextAndArgs = (context: object, ...args: any[]) => Deferred;

  /**
   * A callback provided to a Deferred event such as done, fail, or always.
   * @internal
   */
  type DeferredHandler = (...handlers: AsyncComplete[]) => void;

  /**
   * A function to dynamically handle generating an HTTP response.
   * The response fields should be added to the requestSettings.
   */
  type DynamicResponseHandler = (
    requestSettings: JQueryAjaxSettings,
    done: AsyncComplete | null,
  ) => void;

  /**
   * A method for logging any number of arguments passed in.
   * @internal
   */
  type LogMethod = (...elements: any[]) => void;

  /**
   * A generic callback used internally for forwarding arguments from a
   * jQuery ajax callback.
   * @internal
   */
  type AjaxCallback = (...elements: any[]) => void;

  /** A callback function for JSONP calls. */
  type JSONPCallback = (
    requestSettings: JQueryAjaxSettings,
    callbackContext: object,
    mockHandler: MockHandler | null,
  ) => void;

  /**
   * A method for setting a header with a name and value.
   * @internal
   */
  type SetHeader = (name: string, value: string) => void;

  /**
   * A method for retrieving a header's value by name.
   * @internal
   */
  type GetHeader = (name: string) => string | undefined;

  /**
   * A method for retrieving all headers in a line-delimited and
   * colon-separated string.
   * @internal
   */
  type GetHeaders = () => string;

  /* ================================================================== *
   * Interfaces
   * ================================================================== */

  /**
   * The main Mockjax object, which is also a function for registering
   * new mock ajax handlers.
   */
  interface Mockjax {
    /**
     * Register one or more mock handlers. Returns the handler's UUID, or an
     * array of UUIDs if options was an array.
     */
    (
      options: MockHandler | DynamicMockHandler | Array<MockHandler | DynamicMockHandler>,
    ): string | string[];

    /** Retrieve the current Mockjax global settings. */
    getSettings(): MockjaxSettings;

    /** Reset the Mockjax global settings to their defaults. */
    resetSettings(): void;

    /** Validate the current Mockjax global settings. */
    validateSettings(): void;

    /**
     * Deprecated, use one of the specific `clearByXx()` methods.
     */
    clear(mechanism?: string | RegExp): number;

    /** Clear a single mock handler by its ID. Returns the count cleared. */
    clearById(uuid: string): number;

    /** Clear all mock handlers matching a URL. Returns the count cleared. */
    clearByUrl(url: string | RegExp): number;

    /** Clear all currently registered mock handlers. Returns the count cleared. */
    clearAll(): number;

    /**
     * Deprecated, use `handlers()` with an array of size 1.
     */
    handler(uuid: string): MockHandler | undefined;

    /** Retrieve clones of mock handlers by an array of IDs. */
    handlers(uuids?: string[]): MockHandler[];

    /** Retrieve all mock handlers not yet matched by an ajax call. */
    unfiredHandlers(): MockHandler[];

    /** Retrieve the settings for all ajax calls that have been mocked. */
    mockedAjaxCalls(): JQueryAjaxSettings[];

    /** Retrieve the settings for all ajax calls that have NOT been mocked. */
    unmockedAjaxCalls(): JQueryAjaxSettings[];

    /**
     * Clear all ajax calls that have been retained, regardless of mock status.
     * Returns the number of removed calls.
     */
    clearRetainedAjaxCalls(mockUUIDs?: string[]): number;
  }

  /** Global configuration settings for mockjax. */
  interface MockjaxSettings {
    /** Logger object. */
    logger: { [level: string]: LogMethod };
    /** How much to log (-1 = log nothing). */
    logLevel: number;
    /** Deprecated, use logLevel. */
    logging: number;
    /** Global URL namespace. */
    namespace: string | null;
    /** Default HTTP status code. */
    status: number;
    /** Default status text. */
    statusText: string;
    /** Default response time in ms. */
    responseTime: number;
    /** Default timeout flag. */
    isTimeout: boolean;
    /** Throw error on unmocked requests. */
    throwUnmocked: boolean;
    /** Number of AJAX calls to retain. */
    retainAjaxCalls: number;
    /** Default content type. */
    contentType: string;
    /** Default response function. */
    response: DynamicResponseHandler | null;
    /** Default response text. */
    responseText: any;
    /** Default for XML responses. */
    responseXML: string | null;
    /** Default proxy URL. */
    proxy: string | null;
    /** Deprecated, use proxyMethod. */
    proxyType: HTTPMethod;
    /** Default proxy HTTP method. */
    proxyMethod: HTTPMethod;
    /** Default last modified header. */
    lastModified: string | null;
    /** Default etag header. */
    etag: string;
    /** Deprecated, use responseHeaders. */
    headers: { [header: string]: string };
    /** Default response headers. */
    responseHeaders: { [header: string]: string };
    /** Match handlers in registration order. */
    matchInRegistrationOrder: boolean;
    /** Whether or not to follow 3XX status code redirects. */
    followRedirects: boolean;
  }

  /**
   * Valid options for a jQuery Mockjax handler. Note that any missing
   * options for the Response will be pulled from `$.mockjaxSettings`.
   * One of (url, type, data, or requestHeaders) must be provided.
   */
  interface MockHandler {
    /** The URL to match against. */
    url?: string | RegExp | null;
    /** Deprecated, use method. */
    type?: HTTPMethod | null;
    /** The HTTP method to match against. */
    method?: HTTPMethod | null;
    /** The HTTP request data to match against. */
    data?: DataMatcher | null;
    /** The namespace to override `$.mockjaxSettings`. */
    namespace?: string | null;
    /** The HTTP request headers to match against. */
    requestHeaders?: { [header: string]: string } | null;
    /** The HTTP status code to return (100-599). */
    status?: number | null;
    /** The HTTP status text to return. */
    statusText?: string | null;
    /** The response delay in milliseconds (non-negative). */
    responseTime?: number | null;
    /** The Content-Type header for the response. */
    contentType?: string | null;
    /** A function to call for generating the HTTP Response. */
    response?: DynamicResponseHandler | null;
    /**
     * The response text string to return; if an object, will become
     * stringified JSON.
     */
    responseText?: any;
    /** The URL to proxy the request to. */
    proxy?: string | null;
    /** The HTTP method to use for proxying. */
    proxyType?: HTTPMethod | null;
    /** The HTTP response headers to return. */
    responseHeaders?: { [header: string]: string } | null;
    /** The date to use for the last modification for this request. */
    lastModified: string;
    /** Unique identifier referencing a specific version of the requested data. */
    etag: string;
    /** Fired after the `$.ajax` success method has been called. */
    onAfterSuccess?: CallbackWithRequestSettings | null;
    /** Fired after the `$.ajax` error method has been called. */
    onAfterError?: CallbackWithRequestSettings | null;
    /** Fired after the `$.ajax` complete method has been called. */
    onAfterComplete?: CallbackWithRequestSettings | null;
    /** A UUID for this handler (auto-generated). */
    id: string;
    /** Whether this handler has been used (auto-generated). */
    fired: boolean;
    /** The timestamp when this handler was registered (auto-generated). */
    registeredAt: number;
  }

  /**
   * The current jQuery ajaxSettings (from version 4.0.0), plus the three
   * Mockjax properties (mocked, mockHandlerId, timestamp).
   */
  interface JQueryAjaxSettings {
    /** The location for the request (location.href). */
    url: string;
    /** The HTTP Method ("GET"). */
    method: HTTPMethod;
    /** Is the call asynchronous? (true) */
    async: boolean;
    /** Standard contentType specification for request data. */
    contentType: string;
    /** Time to wait before timeout (or 0 to never timeout). */
    timeout: number;
    /** String for query string or object for body data fields. */
    data: string | any[] | object;
    /** The data type for the call (i.e. script or jsonp). */
    dataType: string;
    /** For basic HTTP auth (null). */
    username?: string | null;
    /** For basic HTTP auth (null). */
    password?: string | null;
    /** Any request headers to send ({}). */
    headers: { [header: string]: string };
    /** Whether this ajax call was mocked. */
    mocked?: boolean | null;
    /** The ID of the mock handler used, if it was mocked. */
    mockHandlerId?: string | null;
    /** The timestamp when this call was initiated. */
    timestamp?: number | null;
  }

  /**
   * A mock of an XMLHttpRequest object that can be used to simulate an ajax
   * call inside of jQuery. This does NOT implement all methods of a real XHR
   * object, or of the jqXHR, so it should not be used outside of Mockjax!
   */
  interface MockXHR {
    /** The mocked HTTP status code. */
    status: number;
    /** The mocked HTTP status text. */
    statusText: string;
    /** The state of the mock XHR. */
    readyState: ReadyState;
    /** For mocked calls this is a no-op function. */
    open: () => void;
    /** Executes a mocked XHR send and sets the "fired" property to true. */
    send: () => void;
    /** Clears the timeout that has been set. */
    abort: () => void;
    /** Sets a single mocked request header. */
    setRequestHeader: SetHeader;
    /** Retrieves a single mocked header. */
    getResponseHeader: GetHeader;
    /** Retrieves all mocked headers as "name: value", separated by newlines. */
    getAllResponseHeaders: GetHeaders;
    /** The ID of the timeout handler for this XHR. */
    responseTimer: number;
  }

  /**
   * A Promise-like object that will execute provided callbacks if supplied.
   * @internal
   */
  interface Deferred {
    /** Resolve a Deferred in a given context. */
    resolveWith: MethodWithContextAndArgs;
    /** Set handlers for when this Deferred is complete. */
    done: DeferredHandler;
    /** Set handlers for when this Deferred succeeds. */
    then: DeferredHandler;
    /** Set handlers for when this Deferred fails. */
    fail: DeferredHandler;
    /** Set handlers for when this Deferred fails. */
    catch: DeferredHandler;
    /** Set handlers for when this Deferred is complete. */
    always: DeferredHandler;
  }

  /**
   * Mock jqXHR which is a combination of XHR and Deferred, typically returned
   * from a `$.ajax()` call.
   * @internal
   */
  interface jqXHR extends MockXHR, Deferred {
    /** A method to retrieve the status code once ready. */
    statusCode: AsyncComplete;
  }

  export default (jq: JQueryStatic, global: object) => Mockjax;
}

declare interface JQueryStatic {
  mockjax: Mockjax;
  mockjaxSettings: MockjaxSettings;
}
