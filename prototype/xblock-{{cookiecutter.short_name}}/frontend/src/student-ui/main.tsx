import { App } from "./App.tsx";
import {
  createXBlockRoot,
  type XBlockConfig,
  type XBlockRuntime,
} from "@opencraft/xblock-react-utils";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";
// This imports the styles as a string so that the createXBlockRoot can automate inserting it into
// the shadow DOM for us.
import styles from "./style.scss?inline";

export const renderBlock = (
  element: Element,
  runtime: XBlockRuntime,
  context: { data: {{cookiecutter.class_name}}Fields; config: XBlockConfig },
) => {
  createXBlockRoot({ runtime, element, config: context.config, styles })(<App {...context.data} />);
};
