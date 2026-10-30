import {
  createXBlockRoot,
  type XBlockConfig,
  type XBlockRuntime,
} from "@opencraft/xblock-react-utils";
import { App } from "./App.tsx";
// This imports the styles as a string so that the createXBlockRoot can automate inserting it into
// the shadow DOM for us.
import styles from "./style.scss?inline";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";
import { XBlockConfigContext } from "@/lib/context.ts";

export const renderBlock = (
  element: Element | null,
  runtime: XBlockRuntime,
  context: { data: {{cookiecutter.class_name}}Fields; config: XBlockConfig },
) => {
  // createXBlockRoot sets up the React app and places it into a new Shadow DOM document root within the
  // HTML document. Shadow DOMs have some isolation from the rest of the page, allowing them to have styles
  // that don't affect elements outside the shadow root.
  createXBlockRoot({ runtime, element, config: context.config, styles })(
    <XBlockConfigContext.Provider value={context.config}>
      <App {...context.data} />
    </XBlockConfigContext.Provider>,
  );
};
