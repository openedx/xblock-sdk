import { jQueryFactory } from "jquery/factory";
import { JSDOM } from "jsdom";
import initMockJax from "jquery-mockjax";

const window = new JSDOM("<html></html>").window;

// @ts-expect-error
window.$ = jQueryFactory(window);

// Stub out AJAX calls in Jquery and add an interface for mocking them.
initMockJax(window.$, window);

window.$.mockjaxSettings.logLevel = 1; // warning messages

// @ts-expect-error
global.$ = window.$;
