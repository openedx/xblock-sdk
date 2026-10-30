import type { SaveStudioBlockParams } from "@opencraft/xblock-react-utils";

const defaultArgs = () => ({
  contentType: "application/json",
  method: "POST",
})

type ModifiedUrlAjaxSettings<T> = Partial<Omit<JQueryAjaxSettings, "data">> & {data: T}
type NormalizedUrlAjaxSettings<T> = Omit<ModifiedUrlAjaxSettings<T>, "data"> & {data: T | string}

/**
 Helper that wraps JQuery's AJAX in a promise so you can use it like modern JavaScript. For convenience
 with use alongside XBlocks, assumes the method is post and the content type is application/json.
 */
export const callServer = <T, C = unknown>(args: ModifiedUrlAjaxSettings<C>): Promise<T> => {
  const resolvedSettings: NormalizedUrlAjaxSettings<C> = {
    ...defaultArgs(),
    ...args,
  }
  if (
    typeof resolvedSettings.data === 'object'
    // typeof null is 'object', believe it or not.
    && resolvedSettings.data !== null
    && resolvedSettings.contentType === "application/json"
  ) {
    resolvedSettings.data = JSON.stringify(resolvedSettings.data)
  }

  const promise = new Promise<T>((resolve, reject) => {
    $.ajax(resolvedSettings as JQueryAjaxSettings).done(resolve).fail(reject);
  })
  return promise;
}

/**
 * Convenience function for saving a block in studio which includes notifications to the runtime of
 * save stop/start.
 */
export const saveStudioBlock = async <T, R = void>({
  saveUrl,
  data,
  runtime,
  errorMessage = "Failed to save configuration",
}: SaveStudioBlockParams<T>): Promise<R> => {
  runtime.notify("save", { state: "start" });
  let result: R;
  try {
    result = await callServer<R, T>({url: saveUrl, data})
    runtime.notify("save", { state: "end" });
  } catch (response: unknown) {
    const message = typeof errorMessage === "function" ? errorMessage(response) : errorMessage;
    runtime.notify("error", {
      title: "Save Error",
      message: message,
    });
    throw response;
  }
  return result;
};
