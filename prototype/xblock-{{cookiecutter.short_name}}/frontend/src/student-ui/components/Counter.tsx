import { useContext } from "react";
import { Button } from "@openedx/paragon";
import { useHandlerUrl } from "@opencraft/xblock-react-utils";
import { AppContext } from "../context.tsx";

export const Counter = () => {
  const incrementUrl = useHandlerUrl("increment");
  const { count, code, setCount } = useContext(AppContext);

  const increment = () => {
    $.post({
      url: incrementUrl,
      data: JSON.stringify({ code }),
      contentType: "application/json",
    }).done((result: { count: number }) => {
      setCount(result.count);
    });
  };

  return (
    <div>
      <p>Count: {count}</p>
      <Button onClick={increment}>Increase</Button>
    </div>
  );
};
