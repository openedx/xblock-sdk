/*
This implements functionality for XBlocks to be able to log
events. Any XBlock can use:
  Logger.log(event_name, event_json)
to place an event in the student event data store. 

Client-side code can also monitor what other client-side code is doing
with Logger.listen.

In the long term, we'd like to move logging to where we use native
JavaScript events and event listeners. This is documentation on
JavaScript events and event listeners:
  https://developer.mozilla.org/en-US/docs/Web/Guide/Events/Creating_and_triggering_events
This is example code for how we might do this:
  https://github.com/pmitros/2013septhack/blob/master/jstrack/framework.html

The advantage of native events is that things like simulations can be
instrumented to generate events which get picked up by complaint
LMSes, while still working on static pages and in non-complaint LMSes.

Our code strategy will be to convert Logger.log to just emit an event,
and likewise, Logger.listen to just register an event listener. Once
this is in all runtimes, Logger will become a convenience function
which just helps structure events and adds some metadata like page
URL.

Conversely, on the XBlock-facing API, we'd like to move eventing into
the XBlocks runtime, so we can automatically annotate events with what
XBlock generated them and other XBlock-local metadata.
*/

;(function() {
    'use strict';
    var Logger = (function() {
        // listeners[event_type][element] -> list of callbacks
        var listeners = {},
            sendRequest, has;

        sendRequest = function(data, options) {
	    console.log(data);
        };

        has = function(object, propertyName) {
            return {}.hasOwnProperty.call(object, propertyName);
        };

        return {
            /**
             * Emits an event.
             */
            log: function(eventType, data, element, requestOptions) {
                var callbacks;

                if (!element) {
                    // null element in the listener dictionary means any element will do.
                    // null element in the Logger.log call means we don't know the element name.
                    element = null;
                }
                // Check to see if we're listening for the event type.
                if (has(listeners, eventType)) {
                    if (has(listeners[eventType], element)) {
                        // Make the callbacks.
                        callbacks = listeners[eventType][element];
                        $.each(callbacks, function(index, callback) {
                            try {
                                callback(eventType, data, element);
                            } catch (err) {
                                console.error({
                                    eventType: eventType,
                                    data: data,
                                    element: element,
                                    error: err
                                });
                            }
                        });
                    }
                }
                // Regardless of whether any callbacks were made, log this event.
                return sendRequest({
                    'event_type': eventType,
                    'event': JSON.stringify(data),
                    'page': window.location.href
                }, requestOptions);
            },

            /**
             * Adds a listener. If you want any element to trigger this listener,
             * do element = null
             */
            listen: function(eventType, element, callback) {
                listeners[eventType] = listeners[eventType] || {};
                listeners[eventType][element] = listeners[eventType][element] || [];
                listeners[eventType][element].push(callback);
            },

            /**
             * Binds `page_close` event.
             */
            bind: function() {
                window.onunload = function() {
                    sendRequest({
                        event_type: 'page_close',
                        event: '',
                        page: window.location.href
                    }, {type: 'GET', async: false});
                };
            }
        };
    }());

    this.Logger = Logger;
    // log_event exists for compatibility reasons and will soon be deprecated.
    this.log_event = Logger.log;
}).call(this);
