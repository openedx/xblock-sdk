import { describe, expect, it } from "vitest";
import userEvent from "@testing-library/user-event";
import { fireEvent } from "@opencraft/xblock-react-utils/testing";
import { initDataFactory, specRender } from "@/lib/specHelpers.tsx";
import { App } from "./App.tsx";

describe("App.tsx", () => {
  it("renders", () => {
    const { screen } = specRender(<App {...initDataFactory()} />);
    screen.getByText("Code");
  });
  it("submits changes to the server", async () => {
    $.mockjax({
      url: "/handler/studio_save",
      method: "POST",
      data: JSON.stringify(
        initDataFactory({
          display_name: "My new block",
          code: "O hai!",
        }),
      ),
      contentType: "application/json",
      responseText: {},
    });
    const user = userEvent.setup();
    const { screen, runtime } = specRender(<App {...initDataFactory()} />);
    const displayName = screen.getByLabelText("Display Name");
    await user.clear(displayName);
    await user.type(displayName, "My new block");
    const codeField = screen.getByLabelText("Code");
    fireEvent.change(codeField, { target: { value: "O hai!" } });
    await user.click(screen.getByText("Save"));
    expect(runtime.notify).toHaveBeenCalledWith("save", { state: "start" });
  });
});
