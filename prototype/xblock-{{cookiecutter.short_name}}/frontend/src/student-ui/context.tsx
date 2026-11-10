import { createContext, useState, type Context, type FC, type PropsWithChildren } from "react";
import type { {{cookiecutter.class_name}}Fields } from "@/types.ts";

interface AppContextExtensions {
  setCount: (arg: number) => void;
}

export const AppContext: Context<{{cookiecutter.class_name}}Fields & AppContextExtensions> = createContext({
  display_name: "{{cookiecutter.class_name}}",
  count: 0,
  code: "beep",
  setCount: (_arg: number) => {},
});

export const AppContextProvider: FC<PropsWithChildren<{{cookiecutter.class_name}}Fields>> = ({
  children,
  ...props
}) => {
  const [count, setCount] = useState(props.count);
  const value = { ...props, count, setCount };
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
