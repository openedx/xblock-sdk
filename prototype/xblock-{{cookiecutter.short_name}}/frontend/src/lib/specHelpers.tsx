import type { ReactNode } from "react";
import { RuntimeContext } from "@opencraft/xblock-react-utils";
import { mockRuntime, render } from "@opencraft/xblock-react-utils/testing";
import { type {{cookiecutter.class_name}}Fields } from "@/types.ts";
import { XBlockConfigContext } from "@/lib/context.ts";

export const initDataFactory = (
  overrides?: Partial<{{cookiecutter.class_name}}Fields>,
): {{cookiecutter.class_name}}Fields => {
  return {
    display_name: "{{cookiecutter.class_name}}",
    count: 0,
    code: "beep",
    ...overrides,
  };
};

export const specRender = (component: ReactNode) => {
  const runtime = mockRuntime();
  const element = document.createElement("div");
  const screen = render(
    <XBlockConfigContext.Provider value={null}>
      <RuntimeContext.Provider value={{"{{"}} runtime, element {{"}}"}}>{component}</RuntimeContext.Provider>
    </XBlockConfigContext.Provider>,
  );
  return { screen, runtime, element };
};
