import * as React from "react";
import { Counter } from "./components/Counter.tsx";
import { AppContextProvider } from "./context.tsx";
import { type {{cookiecutter.class_name}}Fields } from "@/types.ts";

export const App: React.FC<{{cookiecutter.class_name}}Fields> = (props: {{cookiecutter.class_name}}Fields) => {
  return (
    <AppContextProvider {...props}>
      <Counter />
    </AppContextProvider>
  );
};
