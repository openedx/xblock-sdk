import { type XBlockConfig } from "@opencraft/xblock-react-utils";
import { createContext, useContext } from "react";

export const XBlockConfigContext = createContext<XBlockConfig | null>(null);

export const useXBlockConfig = <T extends XBlockConfig>() => {
  return useContext(XBlockConfigContext) as T | null;
};
