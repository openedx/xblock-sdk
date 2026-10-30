import { App } from "./App.tsx";
import {
  createXBlockRoot,
  type XBlockConfig,
  type XBlockRuntime,
} from "@opencraft/xblock-react-utils";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";
import styles from "./style.scss?inline";

export const renderBlock = (
  element: Element,
  runtime: XBlockRuntime,
  context: { data: {{cookiecutter.class_name}}Fields; config: XBlockConfig },
) => {
  createXBlockRoot({ runtime, element, config: context.config, styles })(<App {...context.data} />);
};
