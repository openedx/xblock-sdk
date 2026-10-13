import { useContext } from "react";
import { Button } from "@openedx/paragon";
import { useHandlerUrl, callServer } from "@opencraft/xblock-react-utils";
import { AppContext } from "../context.tsx";

export const Counter = () => {
  const url = useHandlerUrl("increment");
  const { count, code, setCount } = useContext(AppContext);

  const increment = async () => {
    const data = await callServer<{ count: number }>({ url, data: { code } });
    setCount(data.count);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <Button onClick={increment}>Increase</Button>
    </div>
  );
};
