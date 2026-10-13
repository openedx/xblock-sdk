import {
  createXBlockRoot,
  type XBlockConfig,
  type XBlockRuntime,
} from "@opencraft/xblock-react-utils";
import { App } from "./App.tsx";
import styles from "./style.scss?inline";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";
import { XBlockConfigContext } from "@/lib/context.ts";

export const renderBlock = (
  element: Element | null,
  runtime: XBlockRuntime,
  context: { data: {{cookiecutter.class_name}}Fields; config: XBlockConfig },
) => {
  createXBlockRoot({ runtime, element, config: context.config, styles })(
    <XBlockConfigContext.Provider value={context.config}>
      <App {...context.data} />
    </XBlockConfigContext.Provider>,
  );
};
